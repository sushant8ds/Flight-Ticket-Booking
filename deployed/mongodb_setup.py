#!/usr/bin/env python
"""
MongoDB Setup and Migration Script for Django Flight Booking Application
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def check_mongodb_installation():
    """Check if MongoDB is installed and running"""
    try:
        result = subprocess.run(['mongod', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MongoDB is installed")
            return True
        else:
            print("❌ MongoDB is not installed")
            return False
    except FileNotFoundError:
        print("❌ MongoDB is not installed")
        return False

def check_mongodb_running():
    """Check if MongoDB service is running"""
    try:
        result = subprocess.run(['mongo', '--eval', 'db.runCommand("ping")'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MongoDB is running")
            return True
        else:
            print("❌ MongoDB is not running")
            return False
    except FileNotFoundError:
        print("❌ Cannot connect to MongoDB")
        return False

def install_mongodb_macos():
    """Install MongoDB on macOS using Homebrew"""
    print("🔧 Installing MongoDB on macOS...")
    try:
        # Install MongoDB using Homebrew
        subprocess.run(['brew', 'tap', 'mongodb/brew'], check=True)
        subprocess.run(['brew', 'install', 'mongodb-community'], check=True)
        print("✅ MongoDB installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install MongoDB. Please install manually.")
        return False

def start_mongodb_service():
    """Start MongoDB service"""
    print("🚀 Starting MongoDB service...")
    try:
        # Start MongoDB service on macOS
        subprocess.run(['brew', 'services', 'start', 'mongodb/brew/mongodb-community'], check=True)
        print("✅ MongoDB service started")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to start MongoDB service")
        return False

def create_mongodb_database():
    """Create MongoDB database and collections"""
    print("📊 Setting up MongoDB database...")
    try:
        # Create database and basic setup
        mongo_script = """
        use flight_booking_db
        db.createCollection("flight_user")
        db.createCollection("flight_place")
        db.createCollection("flight_week")
        db.createCollection("flight_flight")
        db.createCollection("flight_passenger")
        db.createCollection("flight_ticket")
        
        // Create indexes for better performance
        db.flight_place.createIndex({"code": 1}, {"unique": true})
        db.flight_place.createIndex({"city": 1})
        db.flight_place.createIndex({"country": 1})
        
        db.flight_flight.createIndex({"origin": 1, "destination": 1})
        db.flight_flight.createIndex({"airline": 1})
        db.flight_flight.createIndex({"economy_fare": 1})
        
        db.flight_ticket.createIndex({"ref_no": 1}, {"unique": true})
        db.flight_ticket.createIndex({"user": 1})
        db.flight_ticket.createIndex({"status": 1})
        
        print("Database and collections created successfully")
        """
        
        with open('temp_mongo_setup.js', 'w') as f:
            f.write(mongo_script)
        
        result = subprocess.run(['mongo', 'temp_mongo_setup.js'], 
                              capture_output=True, text=True)
        
        os.remove('temp_mongo_setup.js')
        
        if result.returncode == 0:
            print("✅ MongoDB database setup completed")
            return True
        else:
            print("❌ Failed to setup MongoDB database")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def run_django_migrations():
    """Run Django migrations for MongoDB"""
    print("🔄 Running Django migrations...")
    try:
        # Set MongoDB settings
        os.environ['DJANGO_SETTINGS_MODULE'] = 'capstone.settings_mongodb'
        
        # Run migrations
        subprocess.run([sys.executable, 'manage.py', 'migrate', '--settings=capstone.settings_mongodb'], 
                      check=True)
        print("✅ Django migrations completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        return False

def migrate_existing_data():
    """Migrate existing SQLite data to MongoDB"""
    print("📦 Migrating existing data to MongoDB...")
    try:
        subprocess.run([sys.executable, 'manage.py', 'migrate_to_mongodb', 
                       '--settings=capstone.settings_mongodb'], check=True)
        print("✅ Data migration completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Data migration failed: {e}")
        return False

def update_startup_script():
    """Update startup script to use MongoDB settings"""
    startup_script = """#!/bin/bash
# Django Flight Booking Application Startup Script (MongoDB Version)
# Generated by MongoDB Setup Script

cd /Users/sushant/Flight-Ticket-Booking/deployed
source /Users/sushant/Flight-Ticket-Booking/deployed/venv/bin/activate

echo "🚀 Starting Django Flight Booking Application (MongoDB Version)"
echo "📁 Directory: /Users/sushant/Flight-Ticket-Booking/deployed"
echo "🐍 Python: $(which python)"
echo "🍃 Database: MongoDB"
echo "🌐 URL: http://localhost:8000"
echo ""

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  Starting MongoDB service..."
    brew services start mongodb/brew/mongodb-community
    sleep 3
fi

python manage.py runserver 0.0.0.0:8000 --settings=capstone.settings_mongodb
"""
    
    with open('start_app_mongodb.sh', 'w') as f:
        f.write(startup_script)
    
    os.chmod('start_app_mongodb.sh', 0o755)
    print("✅ MongoDB startup script created: start_app_mongodb.sh")

def main():
    """Main setup function"""
    print("🍃 MongoDB Setup for Django Flight Booking Application")
    print("=" * 60)
    
    # Check current directory
    if not os.path.exists('manage.py'):
        print("❌ Please run this script from the Django project directory")
        sys.exit(1)
    
    # Step 1: Check MongoDB installation
    if not check_mongodb_installation():
        print("\n📥 Installing MongoDB...")
        if not install_mongodb_macos():
            print("❌ Please install MongoDB manually and run this script again")
            sys.exit(1)
    
    # Step 2: Start MongoDB service
    if not check_mongodb_running():
        if not start_mongodb_service():
            print("❌ Please start MongoDB manually and run this script again")
            sys.exit(1)
    
    # Step 3: Create database and collections
    if not create_mongodb_database():
        print("❌ Database setup failed")
        sys.exit(1)
    
    # Step 4: Run Django migrations
    if not run_django_migrations():
        print("❌ Django migrations failed")
        sys.exit(1)
    
    # Step 5: Migrate existing data
    print("\n🔄 Would you like to migrate existing SQLite data to MongoDB? (y/n): ", end="")
    migrate_data = input().lower().strip()
    
    if migrate_data in ['y', 'yes']:
        if not migrate_existing_data():
            print("⚠️  Data migration failed, but MongoDB setup is complete")
    
    # Step 6: Update startup script
    update_startup_script()
    
    print("\n🎉 MongoDB Setup Complete!")
    print("=" * 60)
    print("✅ MongoDB is installed and running")
    print("✅ Database and collections created")
    print("✅ Django configured for MongoDB")
    print("✅ Startup script updated")
    print("\n🚀 To start the application with MongoDB:")
    print("   ./start_app_mongodb.sh")
    print("\n📊 To check MongoDB data:")
    print("   mongo flight_booking_db")
    print("   > db.flight_place.count()")
    print("   > db.flight_flight.count()")

if __name__ == "__main__":
    main()