#!/usr/bin/env python
"""
Test Django application with MongoDB integration
"""
import os
import sys
import django
from mongoengine import connect

def test_mongoengine_models():
    """Test MongoEngine models directly"""
    print("🧪 Testing MongoEngine Models...")
    
    try:
        # Connect to MongoDB
        connect('flight_booking_db', host='mongodb://localhost:27017')
        
        from flight.models_mongoengine import User, Place, Flight, Ticket
        
        # Test queries
        print(f"   Users: {User.objects.count()}")
        print(f"   Places: {Place.objects.count()}")
        print(f"   Flights: {Flight.objects.count()}")
        print(f"   Tickets: {Ticket.objects.count()}")
        
        # Test specific queries
        delhi = Place.objects(code='DEL').first()
        if delhi:
            print(f"   Delhi Airport: {delhi.airport}")
        
        mumbai_flights = Flight.objects(destination__code='BOM').count()
        print(f"   Flights to Mumbai: {mumbai_flights}")
        
        confirmed_tickets = Ticket.objects(status='CONFIRMED').count()
        print(f"   Confirmed Tickets: {confirmed_tickets}")
        
        print("✅ MongoEngine models working correctly")
        return True
        
    except Exception as e:
        print(f"❌ MongoEngine test failed: {e}")
        return False

def test_django_with_mongodb():
    """Test Django application with MongoDB settings"""
    print("\n🧪 Testing Django with MongoDB...")
    
    try:
        # Set MongoDB settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings_mongoengine')
        django.setup()
        
        # Test Django functionality
        from django.conf import settings
        print(f"   Django Settings: {settings.SETTINGS_MODULE}")
        print(f"   MongoDB Database: {settings.MONGODB_SETTINGS['db']}")
        
        # Test Django models (should still work for sessions, etc.)
        from django.contrib.sessions.models import Session
        print(f"   Django Sessions: Available")
        
        print("✅ Django-MongoDB integration working")
        return True
        
    except Exception as e:
        print(f"❌ Django-MongoDB test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flight_search_functionality():
    """Test flight search functionality with MongoDB"""
    print("\n🧪 Testing Flight Search Functionality...")
    
    try:
        from flight.models_mongoengine import Place, Flight
        
        # Test place search
        places = Place.objects(city__icontains='delhi')
        print(f"   Places matching 'delhi': {places.count()}")
        
        # Test flight search
        if places:
            delhi = places.first()
            flights_from_delhi = Flight.objects(origin=delhi)
            print(f"   Flights from Delhi: {flights_from_delhi.count()}")
            
            if flights_from_delhi:
                sample_flight = flights_from_delhi.first()
                print(f"   Sample Flight: {sample_flight.airline} {sample_flight.plane}")
                print(f"   Route: {sample_flight.origin.code} → {sample_flight.destination.code}")
                print(f"   Economy Fare: ${sample_flight.economy_fare}")
        
        print("✅ Flight search functionality working")
        return True
        
    except Exception as e:
        print(f"❌ Flight search test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🍃 Django-MongoDB Integration Test")
    print("=" * 50)
    
    # Test 1: MongoEngine models
    mongoengine_ok = test_mongoengine_models()
    
    # Test 2: Django with MongoDB
    django_ok = test_django_with_mongodb()
    
    # Test 3: Flight search functionality
    search_ok = test_flight_search_functionality()
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print(f"   MongoEngine Models: {'✅ PASS' if mongoengine_ok else '❌ FAIL'}")
    print(f"   Django-MongoDB: {'✅ PASS' if django_ok else '❌ FAIL'}")
    print(f"   Flight Search: {'✅ PASS' if search_ok else '❌ FAIL'}")
    
    if mongoengine_ok and django_ok and search_ok:
        print("\n🎉 All tests passed! MongoDB integration is working correctly!")
        print("🚀 You can now run the application with:")
        print("   ./start_app_mongodb.sh")
    else:
        print("\n❌ Some tests failed. Please check the setup.")

if __name__ == "__main__":
    main()