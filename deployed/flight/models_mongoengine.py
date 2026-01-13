"""
MongoEngine models for Django Flight Booking Application
"""
from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

class User(Document):
    """User model using MongoEngine"""
    username = fields.StringField(max_length=150, unique=True, required=True)
    first_name = fields.StringField(max_length=30)
    last_name = fields.StringField(max_length=30)
    email = fields.EmailField()
    password = fields.StringField(max_length=128)
    is_staff = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)
    date_joined = fields.DateTimeField(default=datetime.now)
    last_login = fields.DateTimeField()

    meta = {
        'collection': 'flight_user',
        'indexes': ['username', 'email']
    }

    def __str__(self):
        return f"{self.id}: {self.first_name} {self.last_name}"

class Place(Document):
    """Airport/City model using MongoEngine"""
    city = fields.StringField(max_length=64, required=True)
    airport = fields.StringField(max_length=64, required=True)
    code = fields.StringField(max_length=3, unique=True, required=True)
    country = fields.StringField(max_length=64, required=True)

    meta = {
        'collection': 'flight_place',
        'indexes': ['code', 'city', 'country']
    }

    def __str__(self):
        return f"{self.city}, {self.country} ({self.code})"

class Week(Document):
    """Week days model using MongoEngine"""
    number = fields.IntField(unique=True, required=True)
    name = fields.StringField(max_length=16, required=True)

    meta = {
        'collection': 'flight_week',
        'indexes': ['number']
    }

    def __str__(self):
        return f"{self.name} ({self.number})"

class Flight(Document):
    """Flight model using MongoEngine"""
    origin = fields.ReferenceField(Place, required=True)
    destination = fields.ReferenceField(Place, required=True)
    depart_time = fields.DateTimeField(required=True)
    depart_day = fields.ListField(fields.ReferenceField(Week))
    duration = fields.StringField()  # Store as string like "2:15:00"
    arrival_time = fields.DateTimeField(required=True)
    plane = fields.StringField(max_length=24, required=True)
    airline = fields.StringField(max_length=64, required=True)
    economy_fare = fields.FloatField(default=0.0)
    business_fare = fields.FloatField(default=0.0)
    first_fare = fields.FloatField(default=0.0)

    meta = {
        'collection': 'flight_flight',
        'indexes': [
            ('origin', 'destination'),
            'airline',
            'economy_fare',
            'depart_time'
        ]
    }

    def __str__(self):
        return f"{self.id}: {self.origin} to {self.destination}"

class Passenger(Document):
    """Passenger model using MongoEngine"""
    GENDER_CHOICES = (
        ('male', 'MALE'),
        ('female', 'FEMALE')
    )
    
    first_name = fields.StringField(max_length=64)
    last_name = fields.StringField(max_length=64)
    gender = fields.StringField(max_length=20, choices=GENDER_CHOICES)

    meta = {
        'collection': 'flight_passenger'
    }

    def __str__(self):
        return f"Passenger: {self.first_name} {self.last_name}, {self.gender}"

class Ticket(Document):
    """Ticket model using MongoEngine"""
    SEAT_CLASS_CHOICES = (
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('first', 'First')
    )

    TICKET_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled')
    )

    user = fields.ReferenceField(User)
    ref_no = fields.StringField(max_length=6, unique=True, required=True)
    passengers = fields.ListField(fields.ReferenceField(Passenger))
    flight = fields.ReferenceField(Flight)
    flight_ddate = fields.DateTimeField()
    flight_adate = fields.DateTimeField()
    flight_fare = fields.FloatField()
    other_charges = fields.FloatField()
    coupon_used = fields.StringField(max_length=15)
    coupon_discount = fields.FloatField(default=0.0)
    total_fare = fields.FloatField()
    seat_class = fields.StringField(max_length=20, choices=SEAT_CLASS_CHOICES)
    booking_date = fields.DateTimeField(default=datetime.now)
    mobile = fields.StringField(max_length=20)
    email = fields.EmailField()
    status = fields.StringField(max_length=45, choices=TICKET_STATUS_CHOICES)

    meta = {
        'collection': 'flight_ticket',
        'indexes': ['ref_no', 'user', 'status', 'booking_date']
    }

    def __str__(self):
        return self.ref_no