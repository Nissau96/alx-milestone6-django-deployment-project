#!/bin/bash

# Celery worker start script
echo "Starting Celery Worker..."

# Activate virtual environment
source venv/bin/activate

# Start Celery worker
exec celery -A deployment_project worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=1000