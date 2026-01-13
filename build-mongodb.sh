#!/bin/bash
# Enhanced build script for MongoDB deployment on Render
set -o errexit

echo "🚀 Starting MongoDB-enabled build for Render deployment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install MongoDB dependencies
echo "🍃 Installing MongoDB dependencies..."
pip install mongoengine pymongo dnspython

# Set Django settings for MongoDB
export DJANGO_SETTINGS_MODULE=capstone.settings_mongodb_render

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run Django migrations (for sessions, admin, etc.)
echo "🔄 Running Django migrations..."
python manage.py migrate

# Initialize MongoDB data if needed
echo "🍃 Initializing MongoDB data..."
python manage.py shell -c "
from flight.mongodb_utils import connect_mongodb, get_database_stats
try:
    connect_mongodb()
    stats = get_database_stats()
    print(f'MongoDB connected. Stats: {stats}')
except Exception as e:
    print(f'MongoDB connection info: {e}')
"

echo "✅ Build completed successfully!"