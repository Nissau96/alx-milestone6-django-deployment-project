#!/bin/bash

# Celery beat start script
echo "Starting Celery Beat Scheduler..."

# Activate virtual environment
source venv/bin/activate

# Start Celery beat
exec celery -A deployment_project beat \
    --loglevel=info \
    --schedule=/tmp/celerybeat-schedule \
    --pidfile=/tmp/celerybeat.pid