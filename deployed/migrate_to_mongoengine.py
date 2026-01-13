#!/usr/bin/env python
"""
Migration script from SQLite to MongoDB using MongoEngine
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
django.setup()

# Import SQLite models
from flight.models import User as SQLiteUser, Place as SQLitePlace, Week as SQLiteWeek
from flight.models import Flight as SQLiteFlight, Passenger as SQLitePassenger, Ticket as SQLiteTicket

# Import MongoEngine models
from flight.models_mongoengine import User as MongoUser, Place as MongoPlace, Week as MongoWeek
from flight.models_mongoengine import Flight as MongoFlight, Passenger as MongoPassenger, Ticket as MongoTicket

def migrate_users():
    """Migrate users from SQLite to MongoDB"""
    print("🔄 Migrating Users...")
    count = 0
    for sqlite_user in SQLiteUser.objects.all():
        try:
            # Check if user already exists
            existing = MongoUser.objects(username=sqlite_user.username).first()
            if not existing:
                mongo_user = MongoUser(
                    username=sqlite_user.username,
                    first_name=sqlite_user.first_name,
                    last_name=sqlite_user.last_name,
                    email=sqlite_user.email,
                    password=sqlite_user.password,
                    is_staff=sqlite_user.is_staff,
                    is_active=sqlite_user.is_active,
                    date_joined=sqlite_user.date_joined,
                    last_login=sqlite_user.last_login
                )
                mongo_user.save()
                count += 1
        except Exception as e:
            print(f"Error migrating user {sqlite_user.username}: {e}")
    
    print(f"✅ Migrated {count} users")
    return count

def migrate_places():
    """Migrate places from SQLite to MongoDB"""
    print("🔄 Migrating Places...")
    count = 0
    for sqlite_place in SQLitePlace.objects.all():
        try:
            # Check if place already exists
            existing = MongoPlace.objects(code=sqlite_place.code).first()
            if not existing:
                mongo_place = MongoPlace(
                    city=sqlite_place.city,
                    airport=sqlite_place.airport,
                    code=sqlite_place.code,
                    country=sqlite_place.country
                )
                mongo_place.save()
                count += 1
        except Exception as e:
            print(f"Error migrating place {sqlite_place.code}: {e}")
    
    print(f"✅ Migrated {count} places")
    return count

def migrate_weeks():
    """Migrate week days from SQLite to MongoDB"""
    print("🔄 Migrating Week days...")
    count = 0
    for sqlite_week in SQLiteWeek.objects.all():
        try:
            # Check if week already exists
            existing = MongoWeek.objects(number=sqlite_week.number).first()
            if not existing:
                mongo_week = MongoWeek(
                    number=sqlite_week.number,
                    name=sqlite_week.name
                )
                mongo_week.save()
                count += 1
        except Exception as e:
            print(f"Error migrating week {sqlite_week.name}: {e}")
    
    print(f"✅ Migrated {count} week days")
    return count

def migrate_flights():
    """Migrate flights from SQLite to MongoDB"""
    print("🔄 Migrating Flights...")
    count = 0
    total = SQLiteFlight.objects.count()
    
    for i, sqlite_flight in enumerate(SQLiteFlight.objects.all()):
        try:
            # Get origin and destination from MongoDB
            mongo_origin = MongoPlace.objects(code=sqlite_flight.origin.code).first()
            mongo_destination = MongoPlace.objects(code=sqlite_flight.destination.code).first()
            
            if not mongo_origin or not mongo_destination:
                print(f"Skipping flight {sqlite_flight.id}: Missing origin or destination")
                continue
            
            # Check if flight already exists
            existing = MongoFlight.objects(
                plane=sqlite_flight.plane,
                airline=sqlite_flight.airline,
                origin=mongo_origin,
                destination=mongo_destination,
                depart_time=datetime.combine(datetime.today().date(), sqlite_flight.depart_time)
            ).first()
            
            if not existing:
                # Convert time to datetime for MongoDB
                depart_datetime = datetime.combine(datetime.today().date(), sqlite_flight.depart_time)
                arrival_datetime = datetime.combine(datetime.today().date(), sqlite_flight.arrival_time)
                
                mongo_flight = MongoFlight(
                    origin=mongo_origin,
                    destination=mongo_destination,
                    depart_time=depart_datetime,
                    duration=str(sqlite_flight.duration) if sqlite_flight.duration else "2:00:00",
                    arrival_time=arrival_datetime,
                    plane=sqlite_flight.plane,
                    airline=sqlite_flight.airline,
                    economy_fare=sqlite_flight.economy_fare or 0.0,
                    business_fare=sqlite_flight.business_fare or 0.0,
                    first_fare=sqlite_flight.first_fare or 0.0
                )
                
                # Add depart days
                depart_days = []
                for day in sqlite_flight.depart_day.all():
                    mongo_day = MongoWeek.objects(number=day.number).first()
                    if mongo_day:
                        depart_days.append(mongo_day)
                
                mongo_flight.depart_day = depart_days
                mongo_flight.save()
                count += 1
            
            if (i + 1) % 1000 == 0:
                print(f"   Processed {i + 1}/{total} flights...")
                
        except Exception as e:
            print(f"Error migrating flight {sqlite_flight.id}: {e}")
    
    print(f"✅ Migrated {count} flights")
    return count

def migrate_passengers():
    """Migrate passengers from SQLite to MongoDB"""
    print("🔄 Migrating Passengers...")
    count = 0
    passenger_mapping = {}
    
    for sqlite_passenger in SQLitePassenger.objects.all():
        try:
            mongo_passenger = MongoPassenger(
                first_name=sqlite_passenger.first_name,
                last_name=sqlite_passenger.last_name,
                gender=sqlite_passenger.gender
            )
            mongo_passenger.save()
            passenger_mapping[sqlite_passenger.id] = mongo_passenger
            count += 1
        except Exception as e:
            print(f"Error migrating passenger {sqlite_passenger.id}: {e}")
    
    print(f"✅ Migrated {count} passengers")
    return count, passenger_mapping

def migrate_tickets(passenger_mapping):
    """Migrate tickets from SQLite to MongoDB"""
    print("🔄 Migrating Tickets...")
    count = 0
    
    for sqlite_ticket in SQLiteTicket.objects.all():
        try:
            # Get user from MongoDB
            mongo_user = None
            if sqlite_ticket.user:
                mongo_user = MongoUser.objects(username=sqlite_ticket.user.username).first()
            
            # Get flight from MongoDB
            mongo_flight = None
            if sqlite_ticket.flight:
                mongo_origin = MongoPlace.objects(code=sqlite_ticket.flight.origin.code).first()
                mongo_destination = MongoPlace.objects(code=sqlite_ticket.flight.destination.code).first()
                
                if mongo_origin and mongo_destination:
                    mongo_flight = MongoFlight.objects(
                        plane=sqlite_ticket.flight.plane,
                        airline=sqlite_ticket.flight.airline,
                        origin=mongo_origin,
                        destination=mongo_destination
                    ).first()
            
            # Check if ticket already exists
            existing = MongoTicket.objects(ref_no=sqlite_ticket.ref_no).first()
            if not existing:
                mongo_ticket = MongoTicket(
                    user=mongo_user,
                    ref_no=sqlite_ticket.ref_no,
                    flight=mongo_flight,
                    flight_ddate=sqlite_ticket.flight_ddate,
                    flight_adate=sqlite_ticket.flight_adate,
                    flight_fare=sqlite_ticket.flight_fare,
                    other_charges=sqlite_ticket.other_charges,
                    coupon_used=sqlite_ticket.coupon_used,
                    coupon_discount=sqlite_ticket.coupon_discount,
                    total_fare=sqlite_ticket.total_fare,
                    seat_class=sqlite_ticket.seat_class,
                    booking_date=sqlite_ticket.booking_date,
                    mobile=sqlite_ticket.mobile,
                    email=sqlite_ticket.email,
                    status=sqlite_ticket.status
                )
                
                # Add passengers
                mongo_passengers = []
                for passenger in sqlite_ticket.passengers.all():
                    if passenger.id in passenger_mapping:
                        mongo_passengers.append(passenger_mapping[passenger.id])
                
                mongo_ticket.passengers = mongo_passengers
                mongo_ticket.save()
                count += 1
                
        except Exception as e:
            print(f"Error migrating ticket {sqlite_ticket.ref_no}: {e}")
    
    print(f"✅ Migrated {count} tickets")
    return count

def main():
    """Main migration function"""
    print("🍃 MongoDB Migration using MongoEngine")
    print("=" * 50)
    
    try:
        # Test MongoDB connection
        from mongoengine import connect
        connect('flight_booking_db', host='mongodb://localhost:27017')
        print("✅ Connected to MongoDB")
        
        # Run migrations
        user_count = migrate_users()
        place_count = migrate_places()
        week_count = migrate_weeks()
        flight_count = migrate_flights()
        passenger_count, passenger_mapping = migrate_passengers()
        ticket_count = migrate_tickets(passenger_mapping)
        
        print("\n" + "=" * 50)
        print("🎉 Migration Summary:")
        print(f"   Users: {user_count}")
        print(f"   Places: {place_count}")
        print(f"   Week days: {week_count}")
        print(f"   Flights: {flight_count}")
        print(f"   Passengers: {passenger_count}")
        print(f"   Tickets: {ticket_count}")
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()