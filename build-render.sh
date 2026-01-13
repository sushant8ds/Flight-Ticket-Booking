#!/bin/bash
set -o errexit

echo "🚀 Starting Render deployment build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-render.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p staticfiles
mkdir -p media

# Set Django settings for Render
export DJANGO_SETTINGS_MODULE=capstone.settings_render

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist (optional)
echo "👤 Creating superuser (if needed)..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF

# Load initial data if needed
echo "📊 Loading initial flight data..."
python manage.py shell << EOF
from flight.models import Place, Flight
if Place.objects.count() == 0:
    print('Loading initial data...')
    exec(open('Data/add_places.py').read())
    print('Initial data loaded successfully')
else:
    print('Data already exists, skipping initial load')
EOF

echo "✅ Build process completed successfully!"