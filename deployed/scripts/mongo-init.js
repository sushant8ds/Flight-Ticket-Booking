// MongoDB initialization script
db = db.getSiblingDB('flight_booking_db');

// Create collections
db.createCollection('flight_user');
db.createCollection('flight_place');
db.createCollection('flight_week');
db.createCollection('flight_flight');
db.createCollection('flight_passenger');
db.createCollection('flight_ticket');

// Create indexes for better performance
db.flight_place.createIndex({'code': 1}, {'unique': true});
db.flight_place.createIndex({'city': 1});
db.flight_place.createIndex({'country': 1});

db.flight_flight.createIndex({'origin': 1, 'destination': 1});
db.flight_flight.createIndex({'airline': 1});
db.flight_flight.createIndex({'economy_fare': 1});

db.flight_ticket.createIndex({'ref_no': 1}, {'unique': true});
db.flight_ticket.createIndex({'user': 1});
db.flight_ticket.createIndex({'status': 1});

print('MongoDB initialization completed successfully');