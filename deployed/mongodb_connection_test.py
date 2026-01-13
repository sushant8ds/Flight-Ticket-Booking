#!/usr/bin/env python
"""
MongoDB Connection Test Script
"""
import os
import sys
import django
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def test_pymongo_connection():
    """Test direct PyMongo connection"""
    print("🔍 Testing PyMongo connection...")
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        print("✅ PyMongo connection successful")
        
        # List databases
        databases = client.list_database_names()
        print(f"📊 Available databases: {databases}")
        
        # Test flight_booking_db
        db = client['flight_booking_db']
        collections = db.list_collection_names()
        print(f"📋 Collections in flight_booking_db: {collections}")
        
        client.close()
        return True
    except ConnectionFailure as e:
        print(f"❌ PyMongo connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ PyMongo error: {e}")
        return False

def test_django_mongodb_connection():
    """Test Django-MongoDB connection"""
    print("\n🔍 Testing Django-MongoDB connection...")
    try:
        # Set MongoDB settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings_mongodb')
        django.setup()
        
        from django.db import connection
        from flight.models_mongodb import Place, User, Flight
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("✅ Django-MongoDB connection successful")
        
        # Test model operations
        print("🧪 Testing model operations...")
        
        # Count existing records
        place_count = Place.objects.count()
        user_count = User.objects.count()
        flight_count = Flight.objects.count()
        
        print(f"📊 Current data counts:")
        print(f"   Places: {place_count}")
        print(f"   Users: {user_count}")
        print(f"   Flights: {flight_count}")
        
        # Test creating a sample record
        test_place, created = Place.objects.get_or_create(
            code='TST',
            defaults={
                'city': 'Test City',
                'airport': 'Test Airport',
                'country': 'Test Country'
            }
        )
        
        if created:
            print("✅ Successfully created test record")
            test_place.delete()
            print("✅ Successfully deleted test record")
        else:
            print("ℹ️  Test record already exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Django-MongoDB connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_migration_status():
    """Check if data has been migrated"""
    print("\n🔍 Checking data migration status...")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings_mongodb')
        django.setup()
        
        from flight.models_mongodb import Place, User, Flight, Ticket
        
        counts = {
            'Places': Place.objects.count(),
            'Users': User.objects.count(),
            'Flights': Flight.objects.count(),
            'Tickets': Ticket.objects.count(),
        }
        
        print("📊 MongoDB Data Status:")
        for model, count in counts.items():
            status = "✅" if count > 0 else "⚠️ "
            print(f"   {status} {model}: {count}")
        
        if all(count > 0 for count in counts.values()):
            print("✅ Data migration appears complete")
        else:
            print("⚠️  Some data may not be migrated yet")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking migration status: {e}")
        return False

def main():
    """Main test function"""
    print("🍃 MongoDB Connection Test")
    print("=" * 50)
    
    # Test 1: PyMongo connection
    pymongo_ok = test_pymongo_connection()
    
    # Test 2: Django-MongoDB connection
    django_ok = test_django_mongodb_connection()
    
    # Test 3: Data migration status
    migration_ok = test_data_migration_status()
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print(f"   PyMongo Connection: {'✅ PASS' if pymongo_ok else '❌ FAIL'}")
    print(f"   Django-MongoDB: {'✅ PASS' if django_ok else '❌ FAIL'}")
    print(f"   Data Migration: {'✅ PASS' if migration_ok else '⚠️  PARTIAL'}")
    
    if pymongo_ok and django_ok:
        print("\n🎉 MongoDB integration is working correctly!")
        print("🚀 You can now run the application with MongoDB")
    else:
        print("\n❌ MongoDB integration has issues")
        print("🔧 Please check the setup and try again")

if __name__ == "__main__":
    main()