#!/bin/bash
echo "Checking Chrome binary at runtime..."
ls -l /usr/local/bin/chrome
echo "Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:"$PORT" app:app