"""
MongoDB-optimized models for Django Flight Booking Application
"""
from djongo import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

# Create your models here.

class User(AbstractUser):
    """Custom User model compatible with MongoDB"""
    def __str__(self):
        return f"{self.id}: {self.first_name} {self.last_name}"

class Place(models.Model):
    """Airport/City model optimized for MongoDB"""
    city = models.CharField(max_length=64)
    airport = models.CharField(max_length=64)
    code = models.CharField(max_length=3, unique=True)
    country = models.CharField(max_length=64)

    class Meta:
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['city']),
            models.Index(fields=['country']),
        ]

    def __str__(self):
        return f"{self.city}, {self.country} ({self.code})"

class Week(models.Model):
    """Week days model"""
    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.name} ({self.number})"

class Flight(models.Model):
    """Flight model optimized for MongoDB with embedded references"""
    origin = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="departures")
    destination = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="arrivals")
    depart_time = models.TimeField()
    depart_day = models.ManyToManyField(Week, related_name="flights_of_the_day")
    duration = models.DurationField(null=True)
    arrival_time = models.TimeField()
    plane = models.CharField(max_length=24)
    airline = models.CharField(max_length=64)
    economy_fare = models.FloatField(null=True, default=0.0)
    business_fare = models.FloatField(null=True, default=0.0)
    first_fare = models.FloatField(null=True, default=0.0)

    class Meta:
        indexes = [
            models.Index(fields=['origin', 'destination']),
            models.Index(fields=['airline']),
            models.Index(fields=['economy_fare']),
            models.Index(fields=['depart_time']),
        ]

    def __str__(self):
        return f"{self.id}: {self.origin} to {self.destination}"

GENDER_CHOICES = (
    ('male', 'MALE'),
    ('female', 'FEMALE')
)

class Passenger(models.Model):
    """Passenger model optimized for MongoDB"""
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)

    def __str__(self):
        return f"Passenger: {self.first_name} {self.last_name}, {self.gender}"

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

class Ticket(models.Model):
    """Ticket model optimized for MongoDB with embedded data"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings", blank=True, null=True)
    ref_no = models.CharField(max_length=6, unique=True)
    passengers = models.ManyToManyField(Passenger, related_name="flight_tickets")
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets", blank=True, null=True)
    flight_ddate = models.DateField(blank=True, null=True)
    flight_adate = models.DateField(blank=True, null=True)
    flight_fare = models.FloatField(blank=True, null=True)
    other_charges = models.FloatField(blank=True, null=True)
    coupon_used = models.CharField(max_length=15, blank=True)
    coupon_discount = models.FloatField(default=0.0)
    total_fare = models.FloatField(blank=True, null=True)
    seat_class = models.CharField(max_length=20, choices=SEAT_CLASS_CHOICES)
    booking_date = models.DateTimeField(default=datetime.now)
    mobile = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=45, blank=True)
    status = models.CharField(max_length=45, choices=TICKET_STATUS_CHOICES)

    class Meta:
        indexes = [
            models.Index(fields=['ref_no']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['booking_date']),
        ]

    def __str__(self):
        return self.ref_no