#!/bin/bash

set -o errexit

set -o nounset

set -o pipefail

python << END
import time
import sys
import psycopg
import os

MAX_WAIT_SECONDS = 60
RETRY_INTERVAL = 5
start_time = time.time()

def check_database():
    try:
        psycopg.connect(
            dbname="${POSTGRES_DB}",
            user="${POSTGRES_USER}",
            password="${POSTGRES_PASSWORD}",
            host="${POSTGRES_HOST}",
            port="${POSTGRES_PORT}",
        )
        return True
    except psycopg.OperationalError as error:
        elapsed = int(time.time() - start_time)
        sys.stderr.write(f"Database connection attempt failed after {elapsed} seconds: {error}\n")
        return False

while True:
    if check_database():
        break

    if time.time() - start_time > MAX_WAIT_SECONDS:
        sys.stderr.write("Error: Database connection could not be established after 60 seconds\n")
        sys.exit(1)

    sys.stderr.write(f"Waiting {RETRY_INTERVAL} seconds before retrying...\n")
    time.sleep(RETRY_INTERVAL)
END

>&2 echo 'PostgreSQL is ready to accept connection'

echo "Running database migrations..."

# * Simple approach: just run alembic upgrade head
# * Alembic will handle creating the version table if it doesn't exist
echo "Running: alembic upgrade head"
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "Migrations completed successfully"
else
    echo "Migration failed with exit code $?"
    exit 1
fi

>&2 echo 'Migrations applied'

exec "$@"
