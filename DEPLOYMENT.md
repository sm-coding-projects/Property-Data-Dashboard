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

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_FILE_SIZE` | `500` | Max file size (MB) |
| `SESSION_TIMEOUT` | `3600` | Session timeout (seconds) |
| `SECRET_KEY` | auto-generated | Flask secret key |
| `REDIS_URL` | `None` | Redis connection URL |
| `RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |

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

### Common Issues

**Out of Memory**:
```bash
# Check memory usage
docker stats
# Increase memory limits in docker-compose.yml
```

**File Upload Fails**:
```bash
# Check file size limits
echo $MAX_FILE_SIZE
# Check disk space
df -h
```

**Session Issues**:
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping
# Check session timeout
echo $SESSION_TIMEOUT
```

### Log Analysis
```bash
# View application logs
docker-compose logs web

# Follow logs in real-time
docker-compose logs -f web

# Filter error logs
docker-compose logs web | grep ERROR
```

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