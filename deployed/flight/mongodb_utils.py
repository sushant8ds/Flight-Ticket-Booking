"""
MongoDB utility functions for Django Flight Booking Application
"""
from mongoengine import connect, disconnect
from django.conf import settings
from flight.models_mongoengine import User, Place, Flight, Ticket, Passenger, Week

# Global connection variable
_mongodb_connected = False

def connect_mongodb():
    """Connect to MongoDB using settings"""
    global _mongodb_connected
    if not _mongodb_connected:
        try:
            # Disconnect any existing connections
            disconnect()
        except:
            pass
        
        # Connect to MongoDB
        mongodb_settings = getattr(settings, 'MONGODB_SETTINGS', {
            'db': 'flight_booking_db',
            'host': 'mongodb://localhost:27017'
        })
        
        connect(**mongodb_settings)
        _mongodb_connected = True
        return True
    return True

def get_places():
    """Get all places from MongoDB"""
    connect_mongodb()
    return Place.objects.all()

def search_places(query):
    """Search places by city, airport, code, or country"""
    connect_mongodb()
    query = query.lower()
    places = Place.objects.filter(
        city__icontains=query
    ) | Place.objects.filter(
        airport__icontains=query
    ) | Place.objects.filter(
        code__icontains=query
    ) | Place.objects.filter(
        country__icontains=query
    )
    return places

def get_flights(origin_code, destination_code, day_number, seat_class='economy'):
    """Get flights between two places on a specific day"""
    connect_mongodb()
    
    # Get places
    origin = Place.objects(code=origin_code.upper()).first()
    destination = Place.objects(code=destination_code.upper()).first()
    
    if not origin or not destination:
        return []
    
    # Get week day
    week_day = Week.objects(number=day_number).first()
    if not week_day:
        return []
    
    # Get flights
    flights = Flight.objects(
        origin=origin,
        destination=destination,
        depart_day=week_day
    )
    
    # Filter by seat class availability
    if seat_class == 'economy':
        flights = flights.filter(economy_fare__gt=0)
    elif seat_class == 'business':
        flights = flights.filter(business_fare__gt=0)
    elif seat_class == 'first':
        flights = flights.filter(first_fare__gt=0)
    
    return flights

def get_flight_by_id(flight_id):
    """Get flight by ID"""
    connect_mongodb()
    return Flight.objects(id=flight_id).first()

def create_ticket(user_data, passengers_data, flight_id, flight_date, seat_class, contact_info):
    """Create a new ticket"""
    connect_mongodb()
    
    # Get flight
    flight = Flight.objects(id=flight_id).first()
    if not flight:
        return None
    
    # Create passengers
    passengers = []
    for passenger_data in passengers_data:
        passenger = Passenger(
            first_name=passenger_data.get('first_name', ''),
            last_name=passenger_data.get('last_name', ''),
            gender=passenger_data.get('gender', '')
        )
        passenger.save()
        passengers.append(passenger)
    
    # Create ticket
    import secrets
    ticket = Ticket(
        ref_no=secrets.token_hex(3).upper(),
        passengers=passengers,
        flight=flight,
        flight_ddate=flight_date,
        seat_class=seat_class,
        mobile=contact_info.get('mobile', ''),
        email=contact_info.get('email', ''),
        status='PENDING'
    )
    
    # Calculate fare
    passenger_count = len(passengers)
    if seat_class == 'economy':
        ticket.flight_fare = flight.economy_fare * passenger_count
    elif seat_class == 'business':
        ticket.flight_fare = flight.business_fare * passenger_count
    elif seat_class == 'first':
        ticket.flight_fare = flight.first_fare * passenger_count
    
    ticket.other_charges = 100.0  # Service fee
    ticket.total_fare = ticket.flight_fare + ticket.other_charges
    
    ticket.save()
    return ticket

def get_user_tickets(username):
    """Get tickets for a user"""
    connect_mongodb()
    # Note: This would need to be adapted based on how you handle users
    # For now, we'll search by email or other identifier
    tickets = Ticket.objects.all()  # Simplified for demo
    return tickets

def get_ticket_by_ref(ref_no):
    """Get ticket by reference number"""
    connect_mongodb()
    return Ticket.objects(ref_no=ref_no).first()

def update_ticket_status(ref_no, status):
    """Update ticket status"""
    connect_mongodb()
    ticket = Ticket.objects(ref_no=ref_no).first()
    if ticket:
        ticket.status = status
        ticket.save()
        return ticket
    return None

def get_database_stats():
    """Get database statistics"""
    connect_mongodb()
    return {
        'users': User.objects.count(),
        'places': Place.objects.count(),
        'flights': Flight.objects.count(),
        'tickets': Ticket.objects.count(),
        'passengers': Passenger.objects.count(),
        'weeks': Week.objects.count(),
    }