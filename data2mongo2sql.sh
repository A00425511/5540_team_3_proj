#!/bin/bash
set -euo pipefail

# Database configuration
DB_USER="u23"
MYSQL_DATABASE="u23"
MONGO_DATABASE="u23"

cd "$(dirname "$0")"

# Get passwords securely from terminal
read -rsp "MySQL password: " MYSQL_PASSWORD
echo
read -rsp "MongoDB password: " MONGO_PASSWORD
echo

export DB_USER MYSQL_DATABASE MONGO_DATABASE
export MYSQL_PASSWORD MONGO_PASSWORD

# Locate JSON file
if [ ! -f project.json ]; then
    echo "Copying project.json..."
    cp /home/u00/sk_public/mcda_files/project5540/2026/project.json .
fi

# Set up Python environment
echo "Setting up Python environment..."

if [ ! -x venv/bin/python ]; then
    python3 -m venv venv
fi

venv/bin/python -m pip install -q \
    pymongo mysql-connector-python

# Create MySQL tables
echo "Step 1: Creating MySQL tables..."

MYSQL_PWD="$MYSQL_PASSWORD" mysql \
    -u "$DB_USER" \
    "$MYSQL_DATABASE" < create_tables.sql

# Import original JSON into MongoDB
echo "Step 2: Importing JSON into MongoDB..."

mongoimport \
    --username "$DB_USER" \
    --password "$MONGO_PASSWORD" \
    --authenticationDatabase admin \
    --db "$MONGO_DATABASE" \
    --collection project_raw \
    --drop \
    --file project.json

# Clean MongoDB data
echo "Step 3: Cleaning MongoDB data..."

mongosh \
    --username "$DB_USER" \
    --password "$MONGO_PASSWORD" \
    --authenticationDatabase admin \
    "$MONGO_DATABASE" \
    --quiet \
    --file clean_mongo.js

# Transfer MongoDB data into MySQL
echo "Step 4: Transferring data into MySQL..."

venv/bin/python process_data.py

echo "All steps completed successfully!"
