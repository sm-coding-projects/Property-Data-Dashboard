# Development Deployment

This section provides detailed instructions for setting up the Property Data Dashboard in a development environment with hot reload, debugging capabilities, and development-optimized configurations.

## Development Environment Setup

### Step 1: Clone and Prepare Repository
```bash
# Clone the repository
git clone <repository-url>
cd Property-Data-Dashboard

# Verify project structure
ls -la
# Expected files: app.py, docker-compose.yml, Dockerfile, requirements.txt
```
**What this does:** Sets up your local development workspace with all necessary project files.

### Step 2: Create Development Environment Configuration
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

### Step 3: Create Development Docker Compose Override
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

### Step 4: Start Development Environment
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

## Development-Specific Environment Variables

### Core Development Variables
| Variable | Development Value | Purpose |
|----------|------------------|---------|
| `DEBUG` | `true` | Enables Flask debug mode with detailed error pages |
| `LOG_LEVEL` | `DEBUG` | Shows all log messages including debug information |
| `SESSION_TIMEOUT` | `7200` (2 hours) | Longer sessions to avoid frequent re-uploads |
| `RATE_LIMIT_ENABLED` | `false` | Disables API rate limiting for testing |
| `MAX_FILE_SIZE` | `1000` (1GB) | Higher limit for testing large files |

### Development Performance Variables
| Variable | Development Value | Purpose |
|----------|------------------|---------|
| `CACHE_TIMEOUT` | `60` | Shorter cache for seeing changes quickly |
| `UPLOAD_TIMEOUT` | `600` | Extended timeout for large file testing |
| `MAX_WORKERS` | `2` | Fewer workers to reduce resource usage |
| `CHUNK_SIZE` | `5000` | Smaller chunks for better debugging |

### Setting Environment Variables
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

## Volume Mounting for Hot Reload

### Understanding Volume Mounting
The development setup uses Docker volume mounting to enable hot reload - changes to your code are immediately reflected in the running container without rebuilding.

### Volume Configuration Explained
```yaml
volumes:
  - .:/app:rw              # Mount current directory to /app with read-write
  - /app/__pycache__       # Exclude Python cache directory
  - /app/node_modules      # Exclude node_modules if present
```

### Hot Reload Behavior
- **Python Files**: Flask automatically restarts when `.py` files change
- **Templates**: HTML templates update immediately without restart
- **Static Files**: CSS/JS files are served directly from mounted volume
- **Configuration**: Changes to `config.py` trigger application restart

### Testing Hot Reload
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

### Volume Mounting Troubleshooting
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

## Debug Mode Configuration

### Enabling Debug Mode
Debug mode provides detailed error information and interactive debugging capabilities.

```bash
# Ensure DEBUG=true in your environment
export DEBUG=true

# Start with debug configuration
docker-compose up --build
```

### Debug Features Available
- **Detailed Error Pages**: Full stack traces with code context
- **Interactive Debugger**: Click on stack trace lines to inspect variables
- **Auto-Reload**: Automatic restart on code changes
- **Template Debugging**: Detailed template error information
- **SQL Query Logging**: Database query logging (if applicable)

### Remote Debugging Setup
For advanced debugging with IDE integration:

```bash
# 1. Install debugpy in container (already included in override)
# 2. Start with debug port exposed
docker-compose up --build

# 3. Connect your IDE to localhost:5678
# VS Code: Use "Python: Remote Attach" configuration
# PyCharm: Create "Python Debug Server" configuration
```

### Debug Configuration Example (VS Code)
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

### Debugging Best Practices
- **Use Breakpoints**: Set breakpoints in your IDE for step-through debugging
- **Log Strategically**: Use `logger.debug()` for development insights
- **Test Error Handling**: Intentionally trigger errors to test error pages
- **Monitor Performance**: Use debug logs to identify slow operations

## Development Workflow Tips and Best Practices

### Daily Development Workflow
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

### Code Development Best Practices

#### 1. Use Development Logging
```python
# Add debug logging to your code
import logging
logger = logging.getLogger(__name__)

def process_data(data):
    logger.debug(f"Processing {len(data)} rows")
    # Your code here
    logger.debug("Processing completed successfully")
```

#### 2. Test with Various File Sizes
```bash
# Create test files of different sizes
head -n 100 large-dataset.csv > small-test.csv      # Small file
head -n 10000 large-dataset.csv > medium-test.csv   # Medium file
# Use full file for large file testing
```

#### 3. Database Development (Redis)
```bash
# Connect to Redis for debugging
docker-compose exec redis redis-cli

# Common Redis commands for development
KEYS *                    # List all keys
GET session:abc123        # Get session data
FLUSHALL                  # Clear all data (development only!)
```

#### 4. Performance Monitoring
```bash
# Monitor resource usage during development
docker stats

# Check memory usage of specific container
docker stats property_analyzer_web --no-stream

# Monitor file processing performance
time curl -X POST http://localhost:8080/api/upload \
  -F "file=@test-data.csv"
```

### Testing and Validation Workflow

#### 1. Automated Testing Setup
```bash
# Run tests in development environment
docker-compose exec web python -m pytest tests/ -v

# Run with coverage
docker-compose exec web python -m pytest tests/ --cov=. --cov-report=html

# Run specific test file
docker-compose exec web python -m pytest tests/test_file_processor.py -v
```

#### 2. Manual Testing Checklist
- [ ] File upload with various CSV formats
- [ ] Large file processing (>100MB)
- [ ] Filter functionality testing
- [ ] Export functionality (CSV/PDF)
- [ ] Session management testing
- [ ] Error handling validation

#### 3. API Testing with curl
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

### Development Environment Maintenance

#### 1. Regular Cleanup
```bash
# Clean up Docker resources weekly
docker system prune -a

# Remove unused volumes
docker volume prune

# Clean up development containers
docker-compose down --volumes --remove-orphans
```

#### 2. Dependency Management
```bash
# Update Python dependencies
docker-compose exec web pip install --upgrade -r requirements.txt

# Add new dependency
echo "new-package==1.0.0" >> requirements.txt
docker-compose up --build

# Check for security vulnerabilities
docker-compose exec web pip-audit
```

#### 3. Configuration Validation
```bash
# Validate environment configuration
docker-compose config

# Check environment variables
docker-compose exec web env | grep -E "(DEBUG|LOG_LEVEL|SESSION_TIMEOUT)"

# Test configuration changes
docker-compose up --build --force-recreate
```

### Common Development Commands

#### Container Management
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

#### Log Management
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

#### Development Database Operations
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

### IDE Integration Tips

#### VS Code Setup
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

#### PyCharm Setup
- Configure Docker Compose as Python interpreter
- Set up remote debugging configuration
- Enable auto-reload for template files
- Configure code formatting with Black

### Troubleshooting Development Issues

#### Hot Reload Not Working
```bash
# Check volume mounting
docker-compose exec web ls -la /app

# Verify file permissions
ls -la app.py

# Force container recreation
docker-compose up --build --force-recreate
```

#### Debug Mode Issues
```bash
# Verify DEBUG environment variable
docker-compose exec web env | grep DEBUG

# Check Flask debug mode
docker-compose exec web python -c "from config import config; print(config.DEBUG)"

# Restart with fresh configuration
docker-compose down && docker-compose up --build
```

#### Performance Issues in Development
```bash
# Reduce file size limits
export MAX_FILE_SIZE=100

# Use fewer workers
export MAX_WORKERS=1

# Increase memory allocation
# Docker Desktop: Settings > Resources > Memory: 8GB+
```

This development deployment guide provides everything needed for efficient development workflow with hot reload, debugging, and best practices for maintaining a productive development environment.