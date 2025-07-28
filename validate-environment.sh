#!/bin/bash

# Environment Configuration Validation Script
# Validates Docker environment configuration for Property Data Dashboard

set -e

echo "🔍 Property Data Dashboard - Environment Validation"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validation functions
validate_required_tools() {
    echo -e "\n📋 Checking Required Tools..."
    
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✓${NC} Docker is installed: $(docker --version)"
    else
        echo -e "${RED}✗${NC} Docker is not installed"
        exit 1
    fi
    
    if command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}✓${NC} Docker Compose is installed: $(docker-compose --version)"
    else
        echo -e "${RED}✗${NC} Docker Compose is not installed"
        exit 1
    fi
}

validate_docker_compose() {
    echo -e "\n🐳 Validating Docker Compose Configuration..."
    
    if [ -f "docker-compose.yml" ]; then
        echo -e "${GREEN}✓${NC} docker-compose.yml exists"
        
        if docker-compose config > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} docker-compose.yml syntax is valid"
        else
            echo -e "${RED}✗${NC} docker-compose.yml has syntax errors"
            docker-compose config
            exit 1
        fi
    else
        echo -e "${RED}✗${NC} docker-compose.yml not found"
        exit 1
    fi
}

validate_dockerfile() {
    echo -e "\n📦 Validating Dockerfile..."
    
    if [ -f "Dockerfile" ]; then
        echo -e "${GREEN}✓${NC} Dockerfile exists"
        
        # Check for required components
        if grep -q "FROM python:" Dockerfile; then
            echo -e "${GREEN}✓${NC} Python base image specified"
        else
            echo -e "${YELLOW}⚠${NC} Python base image not found in Dockerfile"
        fi
        
        if grep -q "EXPOSE 5000" Dockerfile; then
            echo -e "${GREEN}✓${NC} Port 5000 exposed"
        else
            echo -e "${YELLOW}⚠${NC} Port 5000 not explicitly exposed"
        fi
    else
        echo -e "${RED}✗${NC} Dockerfile not found"
        exit 1
    fi
}

validate_environment_variables() {
    echo -e "\n🔧 Validating Environment Variables..."
    
    # Check if .env files exist
    if [ -f ".env" ]; then
        echo -e "${GREEN}✓${NC} .env file found"
    else
        echo -e "${YELLOW}⚠${NC} .env file not found (using defaults)"
    fi
    
    # Validate SECRET_KEY if set
    if [ -n "$SECRET_KEY" ]; then
        if [ ${#SECRET_KEY} -ge 32 ]; then
            echo -e "${GREEN}✓${NC} SECRET_KEY has adequate length (${#SECRET_KEY} characters)"
        else
            echo -e "${YELLOW}⚠${NC} SECRET_KEY is short (${#SECRET_KEY} characters), recommend 32+"
        fi
    else
        echo -e "${YELLOW}⚠${NC} SECRET_KEY not set (will use default)"
    fi
    
    # Check DEBUG setting
    if [ "$DEBUG" = "true" ]; then
        echo -e "${YELLOW}⚠${NC} DEBUG mode is enabled (not recommended for production)"
    else
        echo -e "${GREEN}✓${NC} DEBUG mode is disabled"
    fi
    
    # Check MAX_FILE_SIZE
    if [ -n "$MAX_FILE_SIZE" ]; then
        if [ "$MAX_FILE_SIZE" -gt 0 ] && [ "$MAX_FILE_SIZE" -le 1000 ]; then
            echo -e "${GREEN}✓${NC} MAX_FILE_SIZE is reasonable (${MAX_FILE_SIZE}MB)"
        else
            echo -e "${YELLOW}⚠${NC} MAX_FILE_SIZE might be too large (${MAX_FILE_SIZE}MB)"
        fi
    else
        echo -e "${GREEN}✓${NC} MAX_FILE_SIZE using default (500MB)"
    fi
}

validate_system_resources() {
    echo -e "\n💾 Checking System Resources..."
    
    # Check available memory
    if command -v free &> /dev/null; then
        TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
        if [ "$TOTAL_MEM" -ge 4096 ]; then
            echo -e "${GREEN}✓${NC} Sufficient system memory (${TOTAL_MEM}MB)"
        else
            echo -e "${YELLOW}⚠${NC} Low system memory (${TOTAL_MEM}MB), recommend 4GB+"
        fi
    fi
    
    # Check Docker memory allocation (if Docker Desktop)
    if docker system info 2>/dev/null | grep -q "Total Memory"; then
        DOCKER_MEM=$(docker system info 2>/dev/null | grep "Total Memory" | awk '{print $3}')
        echo -e "${GREEN}✓${NC} Docker memory allocation: ${DOCKER_MEM}"
    fi
    
    # Check disk space
    DISK_SPACE=$(df -h . | awk 'NR==2 {print $4}')
    echo -e "${GREEN}✓${NC} Available disk space: ${DISK_SPACE}"
}

validate_network_ports() {
    echo -e "\n🌐 Checking Network Ports..."
    
    # Check if port 8080 is available
    if lsof -i :8080 &> /dev/null; then
        echo -e "${YELLOW}⚠${NC} Port 8080 is in use"
        echo "    Process using port 8080:"
        lsof -i :8080 | head -2
    else
        echo -e "${GREEN}✓${NC} Port 8080 is available"
    fi
    
    # Check if port 6379 is available (Redis)
    if lsof -i :6379 &> /dev/null; then
        echo -e "${YELLOW}⚠${NC} Port 6379 is in use"
    else
        echo -e "${GREEN}✓${NC} Port 6379 is available"
    fi
}

run_configuration_test() {
    echo -e "\n🧪 Running Configuration Test..."
    
    # Test docker-compose configuration
    if docker-compose config --quiet; then
        echo -e "${GREEN}✓${NC} Docker Compose configuration test passed"
    else
        echo -e "${RED}✗${NC} Docker Compose configuration test failed"
        exit 1
    fi
}

# Main validation flow
main() {
    validate_required_tools
    validate_docker_compose
    validate_dockerfile
    validate_environment_variables
    validate_system_resources
    validate_network_ports
    run_configuration_test
    
    echo -e "\n🎉 Environment Validation Complete!"
    echo -e "${GREEN}✓${NC} Your environment is ready for Docker deployment"
    echo ""
    echo "Next steps:"
    echo "  1. Run: docker-compose up --build"
    echo "  2. Access: http://localhost:8080"
    echo "  3. Test: curl http://localhost:8080/health"
}

# Run main function
main "$@"