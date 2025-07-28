# Property Data Dashboard

A comprehensive, production-ready web application for analyzing and visualizing property sales data from CSV files. Built with Flask, pandas, and modern web technologies, this dashboard provides powerful filtering, visualization, and export capabilities.

## 🚀 Features

### Core Functionality
- **Large File Processing**: Handles CSV files up to 500MB with automatic encoding detection
- **Interactive Filtering**: Multi-dimensional filtering with real-time updates
- **Data Visualization**: KPI cards, charts, and paginated tables
- **Export Capabilities**: CSV and PDF export with filtered data
- **Session Management**: Secure, isolated user sessions with Redis support
- **Production Ready**: Comprehensive error handling, logging, and security features

### Advanced Filtering
- **Suburb Filter**: Multi-select with search functionality
- **Dynamic Purpose Filter**: Shows only purposes available in selected suburbs
- **Price Range**: Precise input boxes for minimum and maximum prices
- **Date Range**: Flexible date filtering with single or range selection
- **Repeat Sales**: Special clustering for properties sold multiple times
- **Pagination**: Variable page sizes (10, 50, 100, 200 properties per page)

### Data Processing Features
- **Automatic Encoding Detection**: Handles various CSV encodings automatically
- **Column Mapping**: Intelligent mapping of CSV columns to expected fields
- **Data Validation**: Comprehensive validation with user-friendly error messages
- **Performance Optimization**: Caching, debouncing, and efficient data processing

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python 3.9, Flask, pandas, Gunicorn
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript, Chart.js
- **Data Storage**: In-memory with optional Redis session storage
- **Containerization**: Docker with Docker Compose
- **Security**: Rate limiting, input validation, CSRF protection

### Project Structure
```
Property-Data-Dashboard/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── error_handler.py      # Centralized error handling
├── file_processor.py     # Robust CSV file processing
├── session_manager.py    # Session management with Redis support
├── rate_limiter.py       # Rate limiting implementation
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-container setup
├── .gitignore          # Git ignore rules
└── templates/
    └── index.html       # Single-page application frontend
```

## 🐳 Docker Deployment

This section provides comprehensive Docker deployment instructions for the Property Data Dashboard, from quick setup to production deployment.

### Prerequisites and System Requirements

Before deploying the Property Data Dashboard with Docker, ensure your system meets the following requirements:

#### Required Software
- **Docker Engine**: Version 20.10.0 or later ([Installation Guide](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0.0 or later (included with Docker Desktop)

#### System Requirements
**Minimum Requirements:**
- **RAM**: 4GB allocated to Docker
- **CPU**: 2 cores
- **Disk Space**: 2GB free space

**Recommended for Large Files:**
- **RAM**: 8GB allocated to Docker
- **CPU**: 4 cores
- **Disk Space**: 5GB free space

#### Docker Resource Configuration
For Docker Desktop (Windows/macOS):
1. Open Docker Desktop → Settings → Resources → Advanced
2. Set Memory to at least 4GB (8GB recommended)
3. Allocate at least 2 CPU cores
4. Apply & Restart

### 🚀 Quick Start Guide

Get the Property Data Dashboard running in under 5 minutes:

#### 1. Get the Application
```bash
git clone <repository-url>
cd Property-Data-Dashboard
```

#### 2. Start the Services
```bash
docker-compose up --build
```
**Expected output:**
```
✓ Container property_analyzer_redis  Created
✓ Container property_analyzer_web    Created
✓ Container property_analyzer_web    Started
✓ Container property_analyzer_redis  Started
```

#### 3. Verify Deployment
```bash
curl http://localhost:8080/health
```
**Expected output:**
```json
{"status": "healthy", "timestamp": "2025-01-25T10:30:00Z"}
```

#### 4. Access the Dashboard
Open your browser and navigate to: **http://localhost:8080**

**Success indicators:**
- ✅ Page loads without errors
- ✅ File upload area is displayed
- ✅ No error messages in browser console

### Development Deployment

For development with hot reload and debugging capabilities:

#### Create Development Override
```bash
cat > docker-compose.override.yml << 'EOF'
version: '3.8'
services:
  web:
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - SESSION_TIMEOUT=7200
      - RATE_LIMIT_ENABLED=false
    volumes:
      - .:/app:rw  # Enable hot reload
    ports:
      - "8080:5000"
      - "5678:5678"  # Debug port
EOF
```

#### Start Development Environment
```bash
docker-compose up --build
```

**Development features:**
- Hot reload on code changes
- Extended session timeout (2 hours)
- Debug logging enabled
- Rate limiting disabled for testing

### Production Deployment

For production environments with security and performance optimizations:

#### Create Production Environment
```bash
cat > .env.prod << 'EOF'
DEBUG=false
SECRET_KEY=your-64-character-secure-secret-key-here
LOG_LEVEL=INFO
MAX_FILE_SIZE=500
SESSION_TIMEOUT=3600
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_ENABLED=true
SECURE_COOKIES=true
FORCE_HTTPS=true
EOF
```

#### Production Docker Compose
```bash
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'
services:
  web:
    build: .
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
      - SECRET_KEY=${SECRET_KEY}
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 1gb
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    restart: unless-stopped
EOF
```

#### Start Production Environment
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### Environment Configuration

#### Complete Environment Variable Reference

| Variable | Type | Default | Development | Production | Docker Context | Description |
|----------|------|---------|-------------|------------|----------------|-------------|
| `DEBUG` | Boolean | `false` | `true` | `false` | Container env | Enable Flask debug mode with detailed error pages |
| `SECRET_KEY` | String | Auto-generated | `dev-key` | **Required** | Container env | Flask secret key for session security and CSRF protection |
| `LOG_LEVEL` | String | `INFO` | `DEBUG` | `INFO` | Container env | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `MAX_FILE_SIZE` | Integer | `500` | `1000` | `500` | Container env | Maximum file upload size in MB |
| `SESSION_TIMEOUT` | Integer | `3600` | `7200` | `3600` | Container env | Session timeout in seconds |
| `REDIS_URL` | String | `None` | `redis://redis:6379/0` | `redis://redis:6379/0` | Service link | Redis connection URL for session storage |
| `RATE_LIMIT_ENABLED` | Boolean | `true` | `false` | `true` | Container env | Enable API rate limiting |
| `UPLOAD_TIMEOUT` | Integer | `300` | `600` | `300` | Container env | File upload timeout in seconds |
| `MAX_WORKERS` | Integer | `4` | `2` | `4` | Container config | Number of Gunicorn worker processes |
| `WORKER_TIMEOUT` | Integer | `120` | `300` | `120` | Container config | Worker timeout in seconds |
| `SECURE_COOKIES` | Boolean | `false` | `false` | `true` | Container env | Force secure cookies (HTTPS only) |
| `FORCE_HTTPS` | Boolean | `false` | `false` | `true` | Container env | Redirect HTTP to HTTPS |

#### Docker-Specific Configuration Examples

**Development with Docker Override:**
```yaml
# docker-compose.override.yml
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
      - .:/app:rw  # Enable hot reload
    ports:
      - "8080:5000"
      - "5678:5678"  # Debug port
```

**Production with Resource Limits:**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  web:
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
      - SECRET_KEY=${SECRET_KEY}
      - SECURE_COOKIES=true
      - FORCE_HTTPS=true
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
```

**Environment File for Docker:**
```bash
# .env.docker
# Docker-specific environment configuration

# Core application settings
DEBUG=false
SECRET_KEY=your-64-character-secure-secret-key
LOG_LEVEL=INFO

# File processing optimized for containers
MAX_FILE_SIZE=500
UPLOAD_TIMEOUT=300
CHUNK_SIZE=10000

# Container networking
REDIS_URL=redis://redis:6379/0
BIND_HOST=0.0.0.0
BIND_PORT=5000

# Container resource management
MAX_WORKERS=4
WORKER_TIMEOUT=120
WORKER_CLASS=sync

# Security for containerized deployment
RATE_LIMIT_ENABLED=true
SECURE_COOKIES=true
FORCE_HTTPS=false  # Set to true behind reverse proxy
```

#### Security Best Practices
```bash
# Generate secure secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Set secure file permissions
chmod 600 .env.prod

# Use strong Redis authentication (production)
REDIS_URL=redis://username:strong-password@redis:6379/0

# Docker secrets management
echo "your-secret-key" | docker secret create property_dashboard_secret -

# Kubernetes secrets
kubectl create secret generic property-dashboard-secret \
  --from-literal=SECRET_KEY=$(openssl rand -hex 32)
```

### Verification and Testing

#### Health Check Verification
```bash
# Test application health
curl http://localhost:8080/health

# Check service status
docker-compose ps

# Monitor logs
docker-compose logs -f web
```

#### Basic Functionality Test
```bash
# Create test CSV file
cat > test-data.csv << 'EOF'
Property locality,Purchase price,Contract date,Primary purpose
Sydney,500000,2024-01-15,Residential
Melbourne,450000,2024-01-20,Residential
EOF

# Test file upload
curl -X POST http://localhost:8080/api/upload -F "file=@test-data.csv"
```

#### Performance Verification
```bash
# Monitor resource usage
docker stats

# Test response times
curl -w "Time: %{time_total}s\n" http://localhost:8080/health
```

### Docker Troubleshooting

#### Common Issues and Solutions

**Port Already in Use:**
```bash
# Find process using port 8080
lsof -i :8080

# Kill conflicting process
sudo kill -9 <PID>

# Or use different port
docker-compose up -p 8081:5000
```

**Out of Memory:**
```bash
# Increase Docker memory allocation
# Docker Desktop → Settings → Resources → Memory: 8GB+

# Check container memory usage
docker stats
```

**Container Won't Start:**
```bash
# Check logs for errors
docker-compose logs web

# Rebuild without cache
docker-compose build --no-cache

# Reset everything
docker-compose down -v
docker-compose up --build
```

**Redis Connection Issues:**
```bash
# Test Redis connectivity
docker-compose exec redis redis-cli ping

# Restart Redis service
docker-compose restart redis

# Check Redis logs
docker-compose logs redis
```

#### Diagnostic Commands
```bash
# View container status
docker-compose ps

# Check container health
docker inspect property_analyzer_web --format='{{.State.Health.Status}}'

# Monitor resource usage
docker stats --no-stream

# Export logs for analysis
docker-compose logs web > application.log
```

### Advanced Configuration

For advanced deployment scenarios including SSL/TLS, load balancing, and cloud deployment, see [DEPLOYMENT.md](DEPLOYMENT.md).

#### Stop the Application
```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 📊 Usage Guide

### Getting Started
1. **Upload Data**: Click the upload area and select a CSV file
2. **Wait for Processing**: Progress bar shows upload and processing status
3. **Explore Data**: Use filters in the left sidebar to analyze your data
4. **Export Results**: Use CSV or PDF export buttons for filtered data

### Filter Options

#### Suburb Filter
- Multi-select dropdown with search functionality
- "Select All" and "Clear All" options
- Real-time search as you type

#### Purpose Filter (Dynamic)
- Shows only purposes available in selected suburbs
- Automatically updates when suburb selection changes
- Prevents invalid suburb/purpose combinations

#### Price Range
- Input boxes for precise minimum and maximum values
- Empty minimum defaults to $0
- Empty maximum defaults to dataset maximum
- Supports any numeric value within data range

#### Date Range
- Flexible date inputs supporting various formats
- Can filter by start date only, end date only, or both
- Debounced input to prevent excessive filtering while typing

#### Repeat Sales
- Special filter for properties sold multiple times
- Clusters same properties together chronologically
- Useful for investment analysis and price tracking

#### Pagination
- Choose from 10, 50, 100, or 200 properties per page
- Maintains selection across filter changes
- Shows current page info and total results

### Data Export
- **CSV Export**: Complete filtered dataset in CSV format
- **PDF Export**: Formatted report with summary statistics (first 1000 rows)
- Both exports respect all active filters

## ⚙️ Configuration

### Docker Deployment Configuration

For comprehensive Docker deployment instructions including environment variables, development setup, and production deployment, see the [Docker Deployment](#-docker-deployment) section above.

### Key Environment Variables

For complete environment variable reference with deployment contexts, see the [Environment Configuration](#environment-configuration) section above.

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode (development only) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MAX_FILE_SIZE` | `500` | Maximum file size in MB |
| `SESSION_TIMEOUT` | `3600` | Session timeout in seconds |
| `REDIS_URL` | `None` | Redis connection URL for session storage |
| `RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `SECRET_KEY` | `auto-generated` | Flask secret key |
| `MAX_WORKERS` | `4` | Number of Gunicorn worker processes |
| `SECURE_COOKIES` | `false` | Force secure cookies (HTTPS only) |
| `FORCE_HTTPS` | `false` | Redirect HTTP to HTTPS |

### Docker Configuration Validation

Validate your Docker configuration before deployment:

```bash
# Validate docker-compose.yml syntax
docker-compose config

# Check environment variables
docker-compose config --services

# Test configuration
docker-compose up --dry-run

# Validate environment file
./validate-environment.sh  # See Environment Configuration section
```

### Non-Docker Development Setup
For development without Docker:

```bash
# Set environment variables
export DEBUG=true
export LOG_LEVEL=DEBUG

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

**Note**: Docker deployment is recommended for both development and production. See [Docker Deployment](#-docker-deployment) for complete instructions.

## 🔒 Security Features

- **Input Validation**: Comprehensive validation of all user inputs
- **File Upload Security**: File type, size, and content validation
- **Rate Limiting**: IP-based rate limiting to prevent abuse
- **Session Security**: Secure session management with automatic cleanup
- **Error Handling**: User-friendly error messages without exposing system details
- **CSRF Protection**: Built-in CSRF protection for all forms

## 🚀 Performance Features

- **Caching**: Intelligent caching of filter results and API responses
- **Debouncing**: Prevents excessive API calls during rapid user input
- **Memory Management**: Automatic cleanup of expired sessions
- **Optimized Processing**: Efficient pandas operations for large datasets
- **Pagination**: Reduces memory usage and improves response times

## 📈 Recent Enhancements

### Dynamic Purpose Filtering
- Purpose filter now shows only purposes available in selected suburbs
- Automatic cleanup of invalid purpose selections
- Caching system for improved performance
- Real-time updates as suburb selections change

### Enhanced Pagination
- Variable page sizes: 10, 50, 100, 200 properties per page
- Improved pagination controls with accurate result counts
- Automatic page reset when changing page size

### Price Input Enhancement
- Replaced sliders with precise input boxes
- Default behavior: 0 (min) to Max (no upper limit)
- Support for exact value entry
- Better keyboard accessibility

### Repeat Sales Clustering
- Properties sold multiple times are grouped together
- Chronological ordering within each property group
- Consistent clustering in both table view and exports

### Robust Error Handling
- Comprehensive error handling with user-friendly messages
- Automatic fallback behaviors for API failures
- Session expiration handling with clear user guidance

## 🧪 Testing

The application includes comprehensive error handling and has been tested with:
- Various CSV file formats and encodings
- Large datasets (300MB+ files)
- Different browser environments
- Edge cases and error conditions
- Security vulnerabilities and performance limits

## 📝 API Endpoints

### Core Endpoints
- `GET /` - Main dashboard interface
- `POST /api/upload` - File upload and processing
- `POST /api/data` - Filtered data retrieval
- `POST /api/export` - Data export (CSV/PDF)
- `POST /api/available-purposes` - Dynamic purpose filtering
- `GET /api/session/<session_id>` - Session validation
- `GET /health` - Health check for monitoring

### Rate Limiting
All API endpoints are protected by rate limiting:
- 100 requests per minute per IP address
- Configurable limits via environment variables
- Graceful handling of rate limit exceeded scenarios

## 🐛 Troubleshooting

### Docker-Specific Issues

For comprehensive Docker troubleshooting including container startup issues, port conflicts, memory problems, and service connectivity, see the [Docker Troubleshooting](#docker-troubleshooting) section above.

#### Container and Service Issues

**Container Won't Start:**
```bash
# Check container status and logs
docker-compose ps
docker-compose logs web

# Rebuild without cache
docker-compose build --no-cache web

# Reset everything
docker-compose down -v
docker-compose up --build
```

**Port Conflicts:**
```bash
# Find process using port 8080
lsof -i :8080

# Use different port
docker-compose up -p 8081:5000

# Kill conflicting process
sudo kill -9 <PID>
```

**Redis Connection Issues:**
```bash
# Test Redis connectivity
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis

# Restart Redis service
docker-compose restart redis
```

**Memory and Performance Issues:**
```bash
# Monitor container resource usage
docker stats

# Check Docker memory allocation
docker system info | grep Memory

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

### Common Application Issues

**File Upload Fails**
- Check file size (max 500MB by default)
- Ensure file is in CSV format
- Verify CSV has required columns (Property locality, Purchase price, etc.)
- Check container logs: `docker-compose logs web`
- Verify disk space: `docker system df`
- See [Docker Troubleshooting](#docker-troubleshooting) for container-related upload issues

**Out of Memory Errors**
- Increase Docker memory allocation to 8GB (see [Prerequisites](#prerequisites-and-system-requirements))
- Use smaller CSV files for testing
- Check available system memory with `docker stats`
- Monitor container memory: `docker stats property_analyzer_web`
- Reduce `MAX_FILE_SIZE` environment variable

**Session Expired**
- Sessions expire after 1 hour by default
- Upload a new file to create a new session
- Configure longer session timeout in environment variables
- Check Redis connectivity if using Redis sessions
- Verify session storage: `docker-compose logs redis`

**Slow Performance**
- Use pagination with smaller page sizes
- Enable Redis for session storage
- Optimize CSV file structure
- Monitor resource usage with `docker stats`
- Check container CPU limits and increase if needed
- Verify network connectivity between services

### Logs and Monitoring
- Application logs: `docker-compose logs web`
- Redis logs: `docker-compose logs redis`
- Health check endpoint: `http://localhost:8080/health`
- Real-time monitoring: `docker-compose logs -f`
- Resource monitoring: `docker stats`

### Advanced Troubleshooting

For detailed troubleshooting procedures including diagnostic commands, log analysis, and performance monitoring, see:
- [Docker Troubleshooting](#docker-troubleshooting) section above
- [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment issues

## 🤝 Contributing

This is a production-ready application with comprehensive features. For modifications:

1. Follow the existing code structure and patterns
2. Add appropriate error handling and logging
3. Update tests for any new functionality
4. Maintain security best practices
5. Update documentation for new features

## 📄 License

This project is provided as-is for property data analysis purposes. Please ensure compliance with data privacy regulations when processing property sales data.

---

**Version**: 2.0.0  
**Last Updated**: January 2025  
**Status**: Production Ready ✅