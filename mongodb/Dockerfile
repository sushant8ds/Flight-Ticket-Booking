# MongoDB Dockerfile for Render deployment
FROM mongo:7.0

# Set environment variables
ENV MONGO_INITDB_ROOT_USERNAME=admin
ENV MONGO_INITDB_DATABASE=flight_booking_db

# Copy initialization script
COPY mongo-init.js /docker-entrypoint-initdb.d/

# Create data directory
RUN mkdir -p /data/db && chown -R mongodb:mongodb /data/db

# Expose MongoDB port
EXPOSE 27017

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD mongosh --eval "db.adminCommand('ping')" || exit 1

# Start MongoDB
CMD ["mongod", "--bind_ip_all"]