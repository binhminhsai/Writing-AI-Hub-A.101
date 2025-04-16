#!/bin/bash
# Script to start the Flask application for Writing AI Hub

# Kill any existing Python processes
pkill -f "python run_dev.py" || true

# Start the application in the background
python run_dev.py > server.log 2>&1 &

# Wait for server to start
sleep 3

# Test if server is running
curl -s http://localhost:8080/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "Server started successfully!"
  echo "Visit http://localhost:8080/ to view the application"
else
  echo "Failed to start server. Check server.log for details."
  cat server.log
fi