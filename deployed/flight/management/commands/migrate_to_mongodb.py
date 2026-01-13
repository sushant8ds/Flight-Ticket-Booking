"""
Django management command to migrate data from SQLite to MongoDB
"""
import os
import sys
import django
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Migrate data from SQLite to MongoDB'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Create backup of existing data before migration',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting migration from SQLite to MongoDB...'))
        
        # Import models from both configurations
        from flight.models import User as SQLiteUser, Place as SQLitePlace, Week as SQLiteWeek
        from flight.models import Flight as SQLiteFlight, Passenger as SQLitePassenger, Ticket as SQLiteTicket
        
        # Switch to MongoDB settings temporarily
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings_mongodb')
        django.setup()
        
        from flight.models_mongodb import User as MongoUser, Place as MongoPlace, Week as MongoWeek
        from flight.models_mongodb import Flight as MongoFlight, Passenger as MongoPassenger, Ticket as MongoTicket
        
        try:
            # Migrate Users
            self.stdout.write('Migrating Users...')
            for sqlite_user in SQLiteUser.objects.all():
                mongo_user, created = MongoUser.objects.get_or_create(
                    username=sqlite_user.username,
                    defaults={
                        'first_name': sqlite_user.first_name,
                        'last_name': sqlite_user.last_name,
                        'email': sqlite_user.email,
                        'is_staff': sqlite_user.is_staff,
                        'is_active': sqlite_user.is_active,
                        'date_joined': sqlite_user.date_joined,
                    }
                )
                if created:
                    mongo_user.set_password(sqlite_user.password)
                    mongo_user.save()
            
            # Migrate Places
            self.stdout.write('Migrating Places...')
            for sqlite_place in SQLitePlace.objects.all():
                MongoPlace.objects.get_or_create(
                    code=sqlite_place.code,
                    defaults={
                        'city': sqlite_place.city,
                        'airport': sqlite_place.airport,
                        'country': sqlite_place.country,
                    }
                )
            
            # Migrate Week days
            self.stdout.write('Migrating Week days...')
            for sqlite_week in SQLiteWeek.objects.all():
                MongoWeek.objects.get_or_create(
                    number=sqlite_week.number,
                    defaults={
                        'name': sqlite_week.name,
                    }
                )
            
            # Migrate Flights
            self.stdout.write('Migrating Flights...')
            for sqlite_flight in SQLiteFlight.objects.all():
                mongo_origin = MongoPlace.objects.get(code=sqlite_flight.origin.code)
                mongo_destination = MongoPlace.objects.get(code=sqlite_flight.destination.code)
                
                mongo_flight, created = MongoFlight.objects.get_or_create(
                    plane=sqlite_flight.plane,
                    airline=sqlite_flight.airline,
                    origin=mongo_origin,
                    destination=mongo_destination,
                    depart_time=sqlite_flight.depart_time,
                    defaults={
                        'duration': sqlite_flight.duration,
                        'arrival_time': sqlite_flight.arrival_time,
                        'economy_fare': sqlite_flight.economy_fare,
                        'business_fare': sqlite_flight.business_fare,
                        'first_fare': sqlite_flight.first_fare,
                    }
                )
                
                if created:
                    # Add depart days
                    for day in sqlite_flight.depart_day.all():
                        mongo_day = MongoWeek.objects.get(number=day.number)
                        mongo_flight.depart_day.add(mongo_day)
            
            # Migrate Passengers
            self.stdout.write('Migrating Passengers...')
            passenger_mapping = {}
            for sqlite_passenger in SQLitePassenger.objects.all():
                mongo_passenger = MongoPassenger.objects.create(
                    first_name=sqlite_passenger.first_name,
                    last_name=sqlite_passenger.last_name,
                    gender=sqlite_passenger.gender,
                )
                passenger_mapping[sqlite_passenger.id] = mongo_passenger
            
            # Migrate Tickets
            self.stdout.write('Migrating Tickets...')
            for sqlite_ticket in SQLiteTicket.objects.all():
                mongo_user = None
                if sqlite_ticket.user:
                    mongo_user = MongoUser.objects.get(username=sqlite_ticket.user.username)
                
                mongo_flight = None
                if sqlite_ticket.flight:
                    mongo_flight = MongoFlight.objects.get(
                        plane=sqlite_ticket.flight.plane,
                        airline=sqlite_ticket.flight.airline,
                        origin__code=sqlite_ticket.flight.origin.code,
                        destination__code=sqlite_ticket.flight.destination.code,
                    )
                
                mongo_ticket = MongoTicket.objects.create(
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
                    status=sqlite_ticket.status,
                )
                
                # Add passengers
                for passenger in sqlite_ticket.passengers.all():
                    if passenger.id in passenger_mapping:
                        mongo_ticket.passengers.add(passenger_mapping[passenger.id])
            
            self.stdout.write(self.style.SUCCESS('Migration completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Migration failed: {str(e)}'))
            raise e