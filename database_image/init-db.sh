#!/bin/bash
set -e

# Check if BIOTA_DB_URL is set
if [ -z "${BIOTA_DB_URL}" ]; then
    echo "ERROR: BIOTA_DB_URL environment variable is not set!"
    echo "Please provide the database download URL via BIOTA_DB_URL environment variable."
    exit 1
fi

# Check if database is already initialized with the same URL
if [ -f "/var/lib/mysql/.db_initialized" ]; then
    STORED_URL=$(cat /var/lib/mysql/.db_initialized)
    if [ "$STORED_URL" = "$BIOTA_DB_URL" ]; then
        echo "Database already initialized with the same URL, skipping download."
        echo "Starting MariaDB..."
        exec docker-entrypoint.sh "$@"
    else
        echo "Database URL has changed!"
        echo "Previous: $STORED_URL"
        echo "New: $BIOTA_DB_URL"
        echo "Removing old database and downloading new one..."
        rm -rf /var/lib/mysql/*
    fi
fi

echo "Downloading and extracting database..."

echo "Downloading from: $BIOTA_DB_URL"

# Download the database zip file
wget -O /tmp/mariadb.zip "$BIOTA_DB_URL"

echo "Download complete, extracting..."

# Extract to temp location
unzip -q /tmp/mariadb.zip -d /tmp/

# Copy contents from mariadb folder to /var/lib/mysql
cp -r /tmp/mariadb/* /var/lib/mysql/

# Fix ownership - all files must be owned by mysql:mysql
echo "Setting correct ownership..."
chown -R mysql:mysql /var/lib/mysql/

# Clean up temp files
rm -rf /tmp/mariadb
rm /tmp/mariadb.zip

# Store the DB URL in the initialization marker file
echo "$BIOTA_DB_URL" > /var/lib/mysql/.db_initialized

echo "Database initialization completed."
echo "Starting MariaDB..."

# Start MariaDB with the original entrypoint
exec docker-entrypoint.sh "$@"

