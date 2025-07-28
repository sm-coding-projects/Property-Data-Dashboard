# Prerequisites and System Requirements

Before deploying the Property Data Dashboard with Docker, ensure your system meets the following requirements and has the necessary tools installed.

## Required Software

### Docker Engine
- **Minimum Version**: Docker Engine 20.10.0 or later
- **Recommended Version**: Docker Engine 24.0.0 or later
- **Installation**: Follow the official Docker installation guide for your platform:
  - [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - [Docker Desktop for macOS](https://docs.docker.com/desktop/install/mac-install/)
  - [Docker Engine for Linux](https://docs.docker.com/engine/install/)

### Docker Compose
- **Minimum Version**: Docker Compose 2.0.0 or later
- **Recommended Version**: Docker Compose 2.20.0 or later
- **Note**: Docker Compose is included with Docker Desktop installations
- **Linux Installation**: If using Docker Engine on Linux, install Docker Compose separately:
  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  ```

## System Requirements

### Minimum Requirements
- **RAM**: 4GB available to Docker
- **CPU**: 2 cores (x86_64 or ARM64 architecture)
- **Disk Space**: 2GB free space for application and dependencies
- **Network**: Internet connection for initial image downloads

### Recommended Requirements
- **RAM**: 8GB available to Docker (for processing large CSV files up to 500MB)
- **CPU**: 4 cores for optimal performance
- **Disk Space**: 5GB free space for data processing and logs
- **Network**: Stable internet connection

### Docker Resource Configuration

#### Docker Desktop (Windows/macOS)
1. Open Docker Desktop
2. Navigate to Settings → Resources → Advanced
3. Configure the following:
   - **Memory**: Set to at least 4GB (8GB recommended)
   - **CPUs**: Allocate at least 2 cores (4 recommended)
   - **Disk Image Size**: Ensure at least 20GB available
4. Click "Apply & Restart"

#### Docker Engine (Linux)
Docker on Linux uses system resources directly. Ensure your system has:
- Sufficient RAM (4GB minimum, 8GB recommended)
- Available CPU cores
- Adequate disk space in `/var/lib/docker`

## Platform-Specific Considerations

### Windows
- **Windows 10/11**: Use Docker Desktop with WSL2 backend (recommended)
- **Windows Server**: Use Docker Engine for Windows Server
- **Hyper-V**: May be required for older Windows versions
- **WSL2**: Recommended for better performance and compatibility

### macOS
- **macOS 10.15+**: Required for Docker Desktop
- **Apple Silicon (M1/M2)**: Fully supported with native ARM64 images
- **Intel Macs**: Use x86_64 images

### Linux
- **Supported Distributions**: Ubuntu 18.04+, Debian 9+, CentOS 7+, RHEL 7+, Fedora 28+
- **Kernel Version**: Linux kernel 3.10 or later
- **Storage Driver**: overlay2 recommended
- **Cgroups**: v1 or v2 supported

## Required Docker Knowledge

### Basic Concepts
Before proceeding, you should be familiar with:
- **Containers**: Understanding what containers are and how they differ from virtual machines
- **Images**: How Docker images work and are built
- **Docker Compose**: Multi-container application orchestration
- **Volumes**: Data persistence and sharing between containers
- **Networks**: Container networking basics

### Essential Commands
You should be comfortable with these Docker commands:
```bash
# Basic container operations
docker run
docker stop
docker ps

# Image management
docker build
docker pull
docker images

# Docker Compose operations
docker-compose up
docker-compose down
docker-compose logs
```

## Learning Resources

### Official Documentation
- [Docker Get Started Guide](https://docs.docker.com/get-started/)
- [Docker Compose Overview](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Interactive Learning
- [Docker 101 Tutorial](https://www.docker.com/101-tutorial)
- [Play with Docker](https://labs.play-with-docker.com/) - Browser-based Docker playground
- [Docker Curriculum](https://docker-curriculum.com/) - Comprehensive beginner guide

### Video Resources
- [Docker Official YouTube Channel](https://www.youtube.com/user/dockerrun)
- [Docker Mastery Course](https://www.udemy.com/course/docker-mastery/) (Third-party)

## Verification Steps

### Verify Docker Installation
```bash
# Check Docker version
docker --version
# Expected output: Docker version 20.10.0 or later

# Check Docker Compose version
docker-compose --version
# Expected output: Docker Compose version 2.0.0 or later

# Test Docker functionality
docker run hello-world
# Should download and run the hello-world container successfully
```

### Verify System Resources
```bash
# Check available memory (Linux/macOS)
free -h

# Check available disk space
df -h

# Check CPU information (Linux)
lscpu

# For Docker Desktop, check resource allocation in Settings → Resources
```

## Common Prerequisites Issues

### Insufficient Memory
**Symptom**: Containers crash or application becomes unresponsive
**Solution**: Increase Docker memory allocation to at least 4GB (8GB recommended)

### Docker Daemon Not Running
**Symptom**: "Cannot connect to the Docker daemon" error
**Solution**: 
- **Docker Desktop**: Start Docker Desktop application
- **Linux**: `sudo systemctl start docker`

### Permission Issues (Linux)
**Symptom**: "Permission denied" when running Docker commands
**Solution**: Add user to docker group:
```bash
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

### Port Conflicts
**Symptom**: "Port already in use" error
**Solution**: Check for conflicting services on ports 8080 and 6379:
```bash
# Check what's using port 8080
lsof -i :8080
netstat -tulpn | grep :8080

# Stop conflicting services or modify docker-compose.yml ports
```

---

**Next Steps**: Once you've verified all prerequisites are met, proceed to the [Quick Start Guide](#quick-start-guide) for immediate deployment or [Development Deployment](#development-deployment) for detailed setup instructions.