#!/bin/bash
# Django Flight Booking Application Startup Script (MongoDB Simple Version)

cd /Users/sushant/Flight-Ticket-Booking/deployed
source /Users/sushant/Flight-Ticket-Booking/deployed/venv/bin/activate

echo "🚀 Starting Django Flight Booking Application (MongoDB Simple Version)"
echo "📁 Directory: /Users/sushant/Flight-Ticket-Booking/deployed"
echo "🐍 Python: $(which python)"
echo "🍃 Database: MongoDB (Direct Connection)"
echo "🌐 URL: http://localhost:8000"
echo ""

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  Starting MongoDB service..."
    brew services start mongodb/brew/mongodb-community
    sleep 3
fi

echo "📊 MongoDB Status:"
mongosh flight_booking_db --quiet --eval "
    print('   Places: ' + db.flight_place.countDocuments())
    print('   Flights: ' + db.flight_flight.countDocuments())
    print('   Users: ' + db.flight_user.countDocuments())
    print('   Tickets: ' + db.flight_ticket.countDocuments())
"
echo ""

# Run Django migrations for sessions/admin (SQLite)
python manage.py migrate --settings=capstone.settings_mongodb_simple

echo "🚀 Starting Django server with MongoDB integration..."
python manage.py runserver 0.0.0.0:8000 --settings=capstone.settings_mongodb_simple