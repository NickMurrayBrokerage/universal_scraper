#!/bin/bash
echo "Entrypoint script started..."
echo "Checking Chrome binary at runtime..."
ls -l /usr/local/bin/chrome
echo "Environment PORT value: $PORT"
# Set PORT to a default if not provided by Render
PORT=${PORT:-10000}
echo "Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:"$PORT" app:app