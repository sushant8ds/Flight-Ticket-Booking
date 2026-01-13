#!/bin/bash
# Kubernetes Deployment Script for Django Flight Booking with MongoDB

set -e

echo "🚀 Starting Kubernetes Deployment for Django Flight Booking Application"
echo "======================================================================="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl."
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

echo "✅ kubectl and Kubernetes cluster are available"

# Build and tag the Docker image
echo "🔨 Building and tagging Docker image..."
docker build -f Dockerfile.mongodb -t flight-booking:mongodb-latest .

# If using a registry, push the image
# docker tag flight-booking:mongodb-latest your-registry/flight-booking:mongodb-latest
# docker push your-registry/flight-booking:mongodb-latest

# Create namespace
echo "📁 Creating namespace..."
kubectl apply -f kubernetes/namespace.yaml

# Deploy MongoDB
echo "🍃 Deploying MongoDB..."
kubectl apply -f kubernetes/mongodb-deployment.yaml

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/mongodb -n flight-booking

# Deploy Django application
echo "🐍 Deploying Django application..."
kubectl apply -f kubernetes/django-deployment.yaml

# Wait for Django app to be ready
echo "⏳ Waiting for Django application to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/django-app -n flight-booking

# Deploy Prometheus
echo "📊 Deploying Prometheus..."
kubectl apply -f kubernetes/prometheus-deployment.yaml

# Wait for Prometheus to be ready
echo "⏳ Waiting for Prometheus to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/prometheus -n flight-booking

# Deploy Grafana
echo "📈 Deploying Grafana..."
kubectl apply -f kubernetes/grafana-deployment.yaml

# Wait for Grafana to be ready
echo "⏳ Waiting for Grafana to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/grafana -n flight-booking

# Get service information
echo "🔍 Getting service information..."
kubectl get services -n flight-booking

echo ""
echo "🎉 Kubernetes deployment completed!"
echo "=================================================================="
echo "📋 Deployed Services:"
kubectl get pods -n flight-booking

echo ""
echo "📊 Service URLs (use kubectl port-forward to access):"
echo "   Django Application:"
echo "     kubectl port-forward -n flight-booking service/django-service 8000:8000"
echo "     Then access: http://localhost:8000"
echo ""
echo "   Prometheus:"
echo "     kubectl port-forward -n flight-booking service/prometheus-service 9090:9090"
echo "     Then access: http://localhost:9090"
echo ""
echo "   Grafana:"
echo "     kubectl port-forward -n flight-booking service/grafana-service 3000:3000"
echo "     Then access: http://localhost:3000 (admin/admin123)"
echo ""
echo "🔍 To view logs:"
echo "   kubectl logs -n flight-booking deployment/django-app -f"
echo "   kubectl logs -n flight-booking deployment/mongodb -f"
echo ""
echo "🛑 To delete all resources:"
echo "   kubectl delete namespace flight-booking"