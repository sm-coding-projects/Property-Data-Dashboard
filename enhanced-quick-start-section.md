# 🚀 Docker Quick Start

Get the Property Data Dashboard running in under 5 minutes with these simple commands.

## Prerequisites

Before starting, ensure you have:
- **Docker** and **Docker Compose** installed ([Installation Guide](https://docs.docker.com/get-docker/))
- **4GB RAM** allocated to Docker (8GB recommended for large files)
- **2GB free disk space** for containers and data

## Quick Deployment

### 1. Get the Application
```bash
git clone <repository-url>
cd Property-Data-Dashboard
```
**What this does**: Downloads the application code and navigates to the project directory.

**Expected output**:
```
Cloning into 'Property-Data-Dashboard'...
remote: Enumerating objects: 45, done.
remote: Total 45 (delta 0), reused 0 (delta 0)
Unpacking objects: 100% (45/45), done.
```

### 2. Start the Services
```bash
docker-compose up --build
```
**What this does**: Builds the application container and starts both the web application and Redis database services.

**Expected output**:
```
Building web
[+] Building 45.2s (12/12) FINISHED
...
Creating property_analyzer_redis ... done
Creating property_analyzer_web   ... done
Attaching to property_analyzer_redis, property_analyzer_web
property_analyzer_web    | * Running on http://0.0.0.0:5000
property_analyzer_redis  | Ready to accept connections
```

### 3. Verify Deployment
```bash
curl http://localhost:8080/health
```
**What this does**: Checks if the application is running and healthy.

**Expected output**:
```json
{"status": "healthy", "timestamp": "2025-01-25T10:30:00Z"}
```

### 4. Access the Dashboard
Open your web browser and navigate to:
```
http://localhost:8080
```

**Success indicators**:
- ✅ Page loads without errors
- ✅ "Property Data Dashboard" title is visible
- ✅ File upload area is displayed
- ✅ No error messages in browser console

## Quick Verification Checklist

After accessing the dashboard, verify these features work:

1. **File Upload**: Drag and drop a CSV file or click to browse
2. **Health Status**: Visit `http://localhost:8080/health` - should return `{"status": "healthy"}`
3. **Logs**: Run `docker-compose logs web` to see application logs
4. **Services**: Run `docker-compose ps` to confirm both services are "Up"

## Next Steps

- **Upload Data**: Try uploading a property CSV file to test the full functionality
- **Customize Configuration**: See [Environment Configuration](#environment-configuration) for advanced settings
- **Production Setup**: Check [Production Deployment](#production-deployment) for production-ready configuration
- **Troubleshooting**: If you encounter issues, see [Docker Troubleshooting](#docker-troubleshooting)

## Stop the Application

When you're done testing:
```bash
docker-compose down
```
**What this does**: Stops and removes the containers while preserving your data.

---

*Need more detailed instructions? See the [Development Deployment](#development-deployment) or [Production Deployment](#production-deployment) sections below.*