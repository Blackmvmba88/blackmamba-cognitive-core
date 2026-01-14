#!/bin/bash
# Quick deployment script for BlackMamba Cognitive Core

set -e

echo "================================================"
echo "BlackMamba Cognitive Core - Deployment Script"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Warning: docker-compose not found, trying 'docker compose'"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "Building Docker image..."
docker build -t blackmamba-cognitive-core:latest .

echo ""
echo "Starting services with Docker Compose..."
$COMPOSE_CMD up -d

echo ""
echo "Waiting for service to be ready..."
sleep 5

# Check health
if curl -f http://localhost:8000/health &> /dev/null; then
    echo ""
    echo "================================================"
    echo "✓ Deployment successful!"
    echo "================================================"
    echo ""
    echo "API is running at: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo "Health Check: http://localhost:8000/health"
    echo ""
    echo "View logs with: $COMPOSE_CMD logs -f"
    echo "Stop services with: $COMPOSE_CMD down"
    echo "================================================"
else
    echo ""
    echo "Warning: Service may not be ready yet"
    echo "Check logs with: $COMPOSE_CMD logs"
fi
