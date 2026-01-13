#!/bin/bash
# Docker Deployment Script for Django Flight Booking with MongoDB

set -e

echo "🚀 Starting Docker Deployment for Django Flight Booking Application"
echo "=================================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Build the MongoDB-enabled Docker image
echo "🔨 Building Django application with MongoDB support..."
docker build -f Dockerfile.mongodb -t flight-booking:mongodb-latest .

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.mongodb.yml down --remove-orphans

# Start the services
echo "🚀 Starting services with Docker Compose..."
docker-compose -f docker-compose.mongodb.yml --env-file .env.docker up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check MongoDB
if docker-compose -f docker-compose.mongodb.yml exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✅ MongoDB is healthy"
else
    echo "❌ MongoDB is not responding"
fi

# Check Django application
if curl -f http://localhost:8000/mongodb/stats > /dev/null 2>&1; then
    echo "✅ Django application is healthy"
else
    echo "❌ Django application is not responding"
fi

# Check Prometheus
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "✅ Prometheus is healthy"
else
    echo "❌ Prometheus is not responding"
fi

# Check Grafana
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Grafana is healthy"
else
    echo "❌ Grafana is not responding"
fi

echo ""
echo "🎉 Deployment completed!"
echo "=================================================================="
echo "📊 Service URLs:"
echo "   Django Application: http://localhost:8000"
echo "   MongoDB Stats: http://localhost:8000/mongodb/stats"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3000 (admin/admin123)"
echo "   Node Exporter: http://localhost:9100"
echo "   cAdvisor: http://localhost:8081"
echo ""
echo "📋 Service Status:"
docker-compose -f docker-compose.mongodb.yml ps

echo ""
echo "🔍 To view logs:"
echo "   docker-compose -f docker-compose.mongodb.yml logs -f [service_name]"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose -f docker-compose.mongodb.yml down"