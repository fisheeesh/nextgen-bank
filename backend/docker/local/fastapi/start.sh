#!/bin/bash

# ? This makes the script to exit immediately if any command exits with a non-zero status,
# ? meaning that the script encouters an error
# ? If we dun set this, the script will continue executing enve after an error occurs
set -o errexit

# ? This unset variables as errors and exit the script immediately
# ? This is going to help us to catch any bugs related to undefined variables
set -o nounset

# ? This ensures that the script exists with a non-zero status if any command in a pipeline fails
# ? By default, our pipeline exit status is that the last command in the pipeline
set -o pipefail

# ? 0.0.0.0 tells the server to listen on all available network interfaces
exec uvicorn app.main:app --app-dir /src/backend --host 0.0.0.0 --port 8000 --reload
