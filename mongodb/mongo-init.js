// MongoDB initialization script for Render deployment
print('Starting MongoDB initialization...');

// Switch to the flight booking database
db = db.getSiblingDB('flight_booking_db');

// Create collections with proper indexes
print('Creating collections and indexes...');

// Users collection
db.createCollection('flight_user');
db.flight_user.createIndex({ 'username': 1 }, { unique: true });
db.flight_user.createIndex({ 'email': 1 }, { unique: true });

// Places collection
db.createCollection('flight_place');
db.flight_place.createIndex({ 'code': 1 }, { unique: true });
db.flight_place.createIndex({ 'city': 1 });
db.flight_place.createIndex({ 'country': 1 });

// Flights collection
db.createCollection('flight_flight');
db.flight_flight.createIndex({ 'origin': 1, 'destination': 1 });
db.flight_flight.createIndex({ 'departure_date': 1 });
db.flight_flight.createIndex({ 'arrival_date': 1 });
db.flight_flight.createIndex({ 'price': 1 });
db.flight_flight.createIndex({ 'flight_number': 1 }, { unique: true });

// Tickets collection
db.createCollection('flight_ticket');
db.flight_ticket.createIndex({ 'user': 1 });
db.flight_ticket.createIndex({ 'ref_no': 1 }, { unique: true });
db.flight_ticket.createIndex({ 'status': 1 });

// Passengers collection
db.createCollection('flight_passenger');
db.flight_passenger.createIndex({ 'ticket': 1 });

// Week collection
db.createCollection('flight_week');

// Create admin user for the application
print('Creating application user...');
db.createUser({
  user: 'flight_app',
  pwd: 'flight_app_password',
  roles: [
    {
      role: 'readWrite',
      db: 'flight_booking_db'
    }
  ]
});

print('MongoDB initialization completed successfully!');

// Insert sample data if collections are empty
if (db.flight_place.countDocuments() === 0) {
    print('Inserting sample places...');
    
    // Sample airports
    db.flight_place.insertMany([
        {
            city: "New York",
            airport: "John F. Kennedy International Airport",
            code: "JFK",
            country: "United States"
        },
        {
            city: "Los Angeles",
            airport: "Los Angeles International Airport", 
            code: "LAX",
            country: "United States"
        },
        {
            city: "London",
            airport: "Heathrow Airport",
            code: "LHR", 
            country: "United Kingdom"
        },
        {
            city: "Paris",
            airport: "Charles de Gaulle Airport",
            code: "CDG",
            country: "France"
        },
        {
            city: "Tokyo",
            airport: "Narita International Airport",
            code: "NRT",
            country: "Japan"
        }
    ]);
    
    print('Sample places inserted successfully!');
}

if (db.flight_week.countDocuments() === 0) {
    print('Inserting week days...');
    
    db.flight_week.insertMany([
        { number: 1, name: "Monday" },
        { number: 2, name: "Tuesday" },
        { number: 3, name: "Wednesday" },
        { number: 4, name: "Thursday" },
        { number: 5, name: "Friday" },
        { number: 6, name: "Saturday" },
        { number: 7, name: "Sunday" }
    ]);
    
    print('Week days inserted successfully!');
}

print('Database setup completed!');