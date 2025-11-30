#!/bin/bash
# Deployment script for Azure App Service
# This script runs during Azure deployment

echo "Starting deployment..."

# Install Python dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Initialize database if needed
if [ "$DB_TYPE" == "sqlite" ]; then
    echo "Initializing SQLite database..."
    python init_db.py
fi

echo "Deployment completed successfully!"
